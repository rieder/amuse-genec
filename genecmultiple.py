"""
Class for making GENEC work with more than one star.
Will create a separate GENEC instance for each star so don't overdo it!
"""

from amuse.datamodel import Particles
from amuse.community.genec import Genec
from amuse.units import units


class GenecParticles:
    def __init__(self, **kwargs):
        self.instances = []
        self.particles = Particles()
        self.kwargs = kwargs

    def add_particle(self, particle):
        self.instances.append(
            Genec(**self.kwargs)
        )
        self.particles.add_particle(
            self.instances[-1].particles.add_particle(particle)
        )
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
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.particles = GenecParticles(**self.kwargs)
        self.instances = self.particles.instances
        self.model_time = 0 | units.Myr

    def evolve_model(self, time):
        while self.model_time < time:
            time_step = self.particles.time_step.min() 
            for instance in self.instances:
                instance.particles.time_step = time_step
                if instance.particles.age.max() < time:
                    instance.evolve_one_step(0)
                    channel = instance.particles.new_channel_to(self.particles.particles)
                    channel.copy()
                if instance.particles.age.max() > self.model_time:
                    self.model_time = instance.particles.age.max()

    def evolve_for(self, time):
        for instance in self.instances:
            instance.evolve_for(0, time)

    def evolve_one_step(self):
        for instance in self.instances:
            instance.evolve_one_step(0)
            channel = instance.particles.new_channel_to(self.particles.particles)
            channel.copy()