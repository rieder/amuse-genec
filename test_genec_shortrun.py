"""
Test to run GENEC "old style" - one (or a few) models at a time.
"""
import sys
import pickle
from amuse.units import units
from amuse.datamodel import Particle
from amuse.community.genec import Genec


def write_genec_model(model):
    "Write a GENEC model to a pickle file"
    with open(
        f"{model['star_name']}-{model['nwmd']:09d}.pkl", 'wb'
    ) as outstream:
        pickle.dump(model, outstream)


def read_genec_model(filename):
    "Read a GENEC model from file"
    with open(filename, 'rb') as instream:
        model = pickle.load(instream)
    return model


def initial_model(
    mass=7.0 | units.MSun,
    metallicity=0.014,
    zams_velocity=0.5,  # this is vwant
    star_name='MyStar',
):
    """
    Generate the initial GENEC model.
    """
    instance = Genec(redirection="none")
    star = Particle(
        mass=mass,
        metallicity=metallicity,
        zams_velocity=zams_velocity,
        star_name=star_name,
        magnetic=False,
        anisotropic=False,
    )
    star_in_code = instance.new_particles.add_particle(star)
    model = star_in_code.get_internal_structure()
    instance.stop()
    return model


def step(model, number_of_steps_per_step=100):
    """
    Evolve GENEC for number_of_steps_per_step and return the new model.
    """
    instance = Genec(redirection="none")
    instance.new_particle_from_model(model)
    for i in range(number_of_steps_per_step):
        instance.evolve_one_step(0)
    model = instance.get_internal_structure(0)
    instance.stop()
    return model


def main():
    "Run GENEC"
    write = True
    number_of_steps = int(sys.argv[1])
    if len(sys.argv) > 2:
        read_genec_model(sys.argv[2])
    else:
        model = initial_model()
        if write:
            write_genec_model(model)
    for i in range(number_of_steps):
        model = step(model)
        if write:
            write_genec_model(model)


if __name__ == "__main__":
    main()
