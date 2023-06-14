"""
Class for making GENEC work with more than one star.
Will create a separate GENEC instance for each star so don't overdo it!
"""

from amuse.datamodel import Particles
from amuse.community.genec import Genec
from amuse.units import units
from amuse.rfi.async_request import AsyncRequestsPool


class GenecParticles:
    def __init__(self, max_number_of_workers=4, **kwargs):
        self.instances = []
        self.particles = Particles()
        self.kwargs = kwargs
        self.max_number_of_workers = max_number_of_workers

    def add_particle(self, particle):
        if len(self.instances) >= self.max_number_of_workers:
            print("Max number of workers would be exceeded, not adding particle")
            return
        self.instances.append(
            Genec(**self.kwargs)
        )
        self.particles.add_particle(
            self.instances[-1].particles.add_particle(particle)
        )
        self.instances[-1].evolve_one_step(0)
        # self.instances[-1].commit_particles()
        return self.particles[-1]

    def add_particles(self, particles):
        number_of_new_particles = len(particles)
        for particle in particles:
            self.add_particle(particle)
        return self.particles[-1:-(1+number_of_new_particles)]

    def __str__(self):
        return self.particles.__str__()

    def __repr__(self):
        return self.particles.__repr__()


class GenecMultiple(Genec):
    def __init__(self, max_number_of_workers=4, **kwargs):
        self.kwargs = kwargs
        self.particles = GenecParticles(
            max_number_of_workers=max_number_of_workers,
            **self.kwargs
        )
        self.parameters = {
            "equal_timesteps": True,
        }
        self.instances = self.particles.instances
        self.model_time = 0 | units.Myr
        self.max_number_of_workers = max_number_of_workers

    def evolve_model(self, time):
        while (time - self.model_time) > (0 | units.yr):
            time_step = self.particles.particles.time_step.min()
            time_step = min(
                time_step,
                time - self.model_time
            )
            if self.parameters['equal_timesteps']:
                for instance in self.instances:
                    instance.particles.time_step = time_step
                    instance.recommit_particles()
            pool = AsyncRequestsPool()
            for i, instance in enumerate(self.instances):
                age = instance.particles.age.in_(units.julianyr)
                if instance.particles.age.max() < time:
                    time_step = instance.particles.time_step.max().in_(units.julianyr)
                    new_time_step = min(
                        time_step,
                        time - instance.particles.age
                    ).in_(units.julianyr)
                    instance.particles.time_step = new_time_step
                    instance.recommit_particles()
                    pool.join(
                        instance.evolve_one_step(0, return_request=True)
                    )
            pool.waitall()
            for instance in self.instances:
                channel = instance.particles.new_channel_to(self.particles.particles)
                channel.copy()
                self.model_time = instance.particles.age.min()

    def evolve_for(self, time):
        for instance in self.instances:
            instance.evolve_for(0, time)

    def evolve_one_step(self):
        for instance in self.instances:
            instance.evolve_one_step(0)
            channel = instance.particles.new_channel_to(self.particles.particles)
            channel.copy()
