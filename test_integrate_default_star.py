import sys
import numpy
import time

from amuse.datamodel import Particle
from amuse.units import units
from amuse.community.genec import Genec
from amuse.io import write_set_to_file, read_set_from_file
from amuse.support.console import set_printing_strategy

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from plot_models import StellarModelPlot

from amuse.community.genec.interface import SPECIES_NAMES
import logging

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
#     datefmt='%Y%m%d %H:%M:%S'
# )
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class NeedToSave:
    def __init__(self):
        self.model = 0
        self.current = {
            'luminosity': 0 | units.LSun,
            'temperature': 0 | units.K,
            'central_temperature': 0 | units.K,
            'central_density': 0 | units.g * units.cm**-3,
            'surface_velocity': 0 | units.kms,
            'mass': 0 | units.MSun,
            'time_step': 0 | units.s,
        }
        for species in SPECIES_NAMES.keys():
            self.current[species] = []
        self.previous = self.current.copy()
        self.derivs = {}
        for key in self.current.keys():
            self.derivs[key] = 1
        return

    def get_values(self):
        return self.current

    @property
    def save_next(self):
        return True

    def update(self, star):
        self.previous = self.current.copy()
        for key in self.current.keys():
            self.current[key] = getattr(star, key)


def read_saved_star_timeline(star_key):
    star = read_set_from_file(f'star-{star_key}.amuse')[0]
    age, radius = star.get_timeline_of_attribute_as_vector('radius')
    print(age.in_(units.yr))
    print(radius.in_(units.RSun))
    return star


def write_backup(
    step,
    star,
    abundances,
    append=True,
):
    if append:
        filename = f'star-{star.key}.amuse'
    else:
        filename = f'star-{star.key}-{step}.amuse'
    write_set_to_file(
        star.as_set(),
        filename,
        timestamp=star.age if append else None,
        append_to_file=append,
        compression=True,
    )

    # For now, abundances aren't part of the single star particle
    # numpy.savez_compressed(
    #     f'star-abundances-{star.key}-{step}.npz',
    #     abundances=abundances,
    # )
    return

MASS_UNIT = units.MSun
LENGTH_UNIT = units.RSun
SPEED_UNIT = units.kms
TIME_UNIT = units.mega(units.julianyr)
MASSLOSS_UNIT = units.MSun / units.julianyr
TEMPERATURE_UNIT = units.K
LUMINOSITY_UNIT = units.LSun
SPEEDUP_UNIT = units.mega(units.julianyr) / units.minute
set_printing_strategy(
    "custom",
    preferred_units=[
        MASS_UNIT, LENGTH_UNIT, TIME_UNIT, SPEED_UNIT, MASSLOSS_UNIT,
        TEMPERATURE_UNIT, LUMINOSITY_UNIT, SPEEDUP_UNIT
    ],
    precision=6,
    prefix="",
    separator=" ",
    # separator=" [",
    suffix="",
    # suffix="]",
)

star_difficult = Particle(
    mass=60 | units.MSun,
    metallicity=0.014,
)

if len(sys.argv) > 1:
    star = read_saved_star_timeline(sys.argv[1])
else:
    star = Particle(
        mass=7.0 | units.MSun,
        metallicity=0.014,
        starname="AmuseStar",
        zams_velocity=0.,
    )
evo = Genec(redirection="none")
# evo = Genec()

star_in_evo = evo.particles.add_particle(star)

font = {
    'size': 8,
}
plt.rc('font', **font)
# iplt.switch_backend('macosx')
plt.ion()

save_every = 10
store_every = 1
plot_time = 10 | units.s
plot_models = 1
step = 0

model_of_last_save = 0
model_of_last_plot = 0
time_start = time.time() | units.s
time_of_last_plot = 0 | units.s
age_of_last_plot = star_in_evo.age

plotting = None
plotting = StellarModelPlot(star_in_evo)

# evo.parameters.nzmod = 100

# print("age   mass   radius   temp   lum   phase   vequat   h0   vwant  xcn")
while True:
    time_elapsed = (time.time() | units.s) - time_start
    star = star_in_evo.copy()
    # number_of_zones = star_in_evo.get_number_of_zones()
    # density_profile = star_in_evo.get_density_profile()
    # radius_profile = star_in_evo.get_radius_profile()
    # temperature_profile = star_in_evo.get_temperature_profile()
    # luminosity_profile = star_in_evo.get_luminosity_profile()
    # pressure_profile = star_in_evo.get_pressure_profile()
    chemical_abundance_profile = star_in_evo.get_chemical_abundance_profiles()

    # print(evo.particles[0])
    # print(evo.particles[0].get_number_of_species())
    # print(evo.particles[0].get_names_of_species())
    # print(evo.particles[0].get_mass_profile())
    # exit()
    print(
        star.age.in_(units.Myr),
        star.mass.in_(units.MSun),
        star.radius.in_(units.RSun),
        star.temperature.in_(units.K),
        star.luminosity.in_(units.LSun),
        star.surface_velocity,
    )
    print(f"step: {step} time: {star.age} timestep: {star.time_step}")
    if (step % store_every == 0) and plotting is not None:
        plotting.update(star_in_evo)
        if (
            (time_elapsed - time_of_last_plot) > plot_time
            or step - model_of_last_plot > plot_models
        ):
            speed = (
                (star.age - age_of_last_plot).value_in(units.Myr)
                / (time_elapsed - time_of_last_plot).value_in(units.minute)
            ) | units.Myr / units.minute
            plotting.plot_all(speed=speed, step=step)
            model_of_last_plot = step
            time_of_last_plot = time_elapsed
            age_of_last_plot = star.age

    if step % save_every == 0:
        write_backup(
            step,
            star,
            # density_profile,
            # radius_profile,
            # temperature_profile,
            # luminosity_profile,
            # pressure_profile,
            chemical_abundance_profile,
        )

    age_previous = star_in_evo.age
    star_in_evo.evolve_one_step()
    # print(f"Condition: {evo.parameters.stopping_condition}")
    # if evo.parameters.stopping_condition != "none":
    #     # star_in_evo.age == age_previous:
    #     if step > 1:
    #         print("Stopping - not evolving!")
    #         print(f"Condition: {evo.parameters.stopping_condition}")
    #         break
    step += 1

runtime = (time.time() | units.s) - time_start
print(
    f"Running {step} models took {runtime.value_in(units.minute)} minutes"
)
