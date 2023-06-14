import sys
from amuse.units import units
from amuse.datamodel import Particles
from amuse.community.genec import Genec
from genecmultiple import GenecMultiple
from amuse.support.console import set_printing_strategy

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
    datefmt='%Y%m%d %H:%M:%S'
)
LOGGER = logging.getLogger(__name__)


set_printing_strategy(
    'custom',
    preferred_units=[units.s, units.RSun, units.MSun, units.kms, units.K]
)

age = float(sys.argv[1]) | units.mega(units.julianyr)
sync = True
if sys.argv[2] == "0":
    sync = False
verbose = False
if sys.argv[3] == "1":
    verbose = True

stars = Particles(mass=(7.0, 8.0, 9.0, 10.0) | units.MSun)
if verbose:
    x = GenecMultiple(redirection="none")
else:
    x = GenecMultiple()
x.parameters["equal_timesteps"] = sync
print(x.parameters)
stars_in_code = x.particles.add_particles(stars)

# x.evolve_one_step()
# x.evolve_model(0.1 | units.mega(units.julianyr))
x.evolve_model(age)
print(x.particles)
