from amuse.community.genec import Genec
from amuse.lab import *
from genecmultiple import GenecMultiple

stars = Particles(mass=(7.0, 8.0, 9.0, 10.0, 11.0) | units.MSun)
# x = GenecMultiple(redirection="none")
x = GenecMultiple()
print(x.parameters)
x.parameters["equal_timesteps"] = False
stars_in_code = x.particles.add_particles(stars)

# x.evolve_one_step()
x.evolve_model(0.0123 | units.mega(units.julianyr))
print(x.particles)
