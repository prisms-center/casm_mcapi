"""Create Samples"""

# this script creates a 'CASM Monte Carlo Calculation' process
# and uploads the results files

import os

# Note assume throughout that mcapi.Project.local_abspath is set with local
# Materials Commons project directory tree location

# The following create and set measurments, updating 'create_sample_process'

def _set_measurement(create_sample_process, attribute, measurement_data, name=None):
    if not name:
        name = attribute

    if not "name" in measurement_data:
        measurement_data['name'] = name

    if not "attribute" in measurement_data:
        measurement_data['attribute'] = attribute

    if not "unit" in measurement_data:
        measurement_data['unit'] = ""

    measurement = create_sample_process.create_measurement(data=measurement_data)

    measurement_property = {
        "name": name,
        "attribute": attribute
    }

    return create_sample_process.set_measurements_for_process_samples(
        measurement_property, [measurement])


def _add_integer_measurement(create_sample_process, attribute, value, name=None):
    if not name:
        name = attribute

    measurement_data = {
        "name": name,
        "attribute": attribute,
        "otype": "integer",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attribute, measurement_data, name)


def _add_number_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "number",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)


def _add_boolean_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "boolean",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)


def _add_string_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "string",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

def _add_selection_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "selection",
        "value": value,
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

def _add_numpy_matrix_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "matrix",
        "value": {
            "dimensions": list(value.shape),
            "otype":  "float",
            "value": value.tolist()
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

def _add_vector_measurement(create_sample_process, attrname, value, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "vector",
        "value": {
            "dimensions": len(value),
            "otype":  "float",
            "value": value
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

def _add_list_measurement(create_sample_process, attrname, value, value_type, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "vector",
        "value": {
            "dimensions": len(value),
            "otype":  value_type,
            "value": value
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

def _add_file_measurement(create_sample_process, attrname, mcfile, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "file",
        "value": {
            "file_id": mcfile.id,
            "file_name": mcfile.name
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)

# NOTE: no covering test or example for this function - probably works - Terry, Jan 20, 2016
def _add_sample_measurement(create_sample_process, attrname, sample, name=None):
    measurement_data = {
        "attribute": attrname,
        "otype": "sample",
        "value": {
            "sampled_id": sample.id,
            "sample_name": sample.name,
            "property_set_id": sample.property_set_id
        },
        "is_best_measure": True
    }
    return _set_measurement(create_sample_process, attrname, measurement_data, name)


def _add_file(proj, local_file_abspath, filename=None):
    """
    Upload a file, matching local directory structure and creating intermediate
    remote directories as necessary. Uses local filename.

    Arguments:

        proj: mcapi.Project object

        local_file_abspath: str
          absolute path to local file

        filename: str (default=os.path.basename(local_file_abspath))
          name to give file on Materials Commons

    """
    file_relpath = os.path.relpath(proj.local_abspath, local_file_abspath)
    top = proj.get_top_directory()

    # get mcapi.Directory to add file, creating intermediates as necessary
    mcdir = top.get_descendent_list_by_path(os.path.dirname(file_relpath))[-1]

    if filename is None:
        filename = os.path.basename(local_file_abspath)
    return mcdir.add_file(filename, local_file_abspath)


def create_prim_sample(expt, casm_proj):
    """
    Create a CASM Primitive Crystal Structure Sample

    Assumes expt.proj.local_abspath exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        casm_proj: casm.project.Project object

    Returns:

        create_sample_process: mcapi.Process instance
          The Process that created the sample
    """

    ## Create Sample
    create_sample_process = expt.create_process_from_template("global_Primitive Crystal Structure")

    # Sample attributes (how to check names?):
    # "name"
    _add_string_measurement(create_sample_process, 'name', casm_proj.name)

    prim = casm_proj.prim

    # "lattice"
    #     "matrix"
    #     "parameters" (a, b, c, alpha, beta, gamma)
    #     "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal",
    #               "hexagonal", "rhombohedral", "cubic")
    #     "symmetry" (Schoenflies symbol)
    _add_numpy_matrix_measurement(
        create_sample_process,
        'lattice_matrix',
        prim.lattice_matrix)

    _add_vector_measurement(
        create_sample_process,
        'lattice_parameters',
        prim.lattice_parameters)

    _add_string_measurement(
        create_sample_process,
        'lattice_point_group_schonflies',
        prim.lattice_symmetry_s)

    _add_string_measurement(
        create_sample_process,
        'lattice_point_group_hermann_mauguin',
        prim.lattice_symmetry_hm)

    _add_string_measurement(
        create_sample_process,
        'lattice_system',
        prim.lattice_system)

    # "space_group"
    #      "point_group_schonflies"
    #      "point_group_hermann_mauguin"
    #      "number"
    #      "crystal_family" ("triclinic", "monoclinic", "orthorhombic",
    #                        "tetragonal", "hexagonal", "cubic")
    #      "crystal_system" ("triclinic", "monoclinic", "orthorhombic",
    #                        "tetragonal", "hexagonal", "trigonal", "cubic")
    _add_string_measurement(
        create_sample_process,
        'crystal_point_group_schonflies',
        prim.crystal_symmetry_s)

    _add_string_measurement(
        create_sample_process,
        'crystal_point_group_hermann_mauguin',
        prim.crystal_symmetry_hm)

    _add_string_measurement(
        create_sample_process,
        'crystal_family',
        prim.crystal_family)

    _add_string_measurement(
        create_sample_process,
        'crystal_system',
        prim.crystal_system)

    # right now, this is a string giving a range of possible values based on the
    #   crystal point group
    _add_string_measurement(
        create_sample_process,
        'space_group_number',
        prim.space_group_number)

    # "casm_prim_file"
    mcfile = _add_file(expt.proj, casm_proj.dir.prim())
    _add_file_measurement(create_sample_process, 'casm_prism_file', mcfile)

    # "elements" - currently only elemental components are allowed
    _add_list_measurement(
        create_sample_process,
        'elements',
        prim.elements,
        'string')

    # "n_elements"
    _add_integer_measurement(
        create_sample_process,
        'n_elements',
        len(prim.n_elements))

    # "components" - currently only elemental components are allowed
    _add_list_measurement(
        create_sample_process,
        'components',
        prim.components,
        'string')

    # "n_components"
    _add_integer_measurement(
        create_sample_process,
        'n_components',
        len(prim.components))

    # "n_independent_compositions"
    _add_integer_measurement(
        create_sample_process,
        'n_independent_compositions',
        prim.n_independent_compositions)

    # "degrees_of_freedom" ("occupation", "displacement", "strain")
    _add_string_measurement(
        create_sample_process,
        'degrees_of_freedom',
        prim.degrees_of_freedom)

    return create_sample_process


def create_composition_axes_sample(expt, casm_proj, prim, axes_name):
    """
    Create a CASM Composition Axes Sample

    Assumes expt.proj.local_abspath exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment instance

        casm_proj: casm.project.Project instance

        prim: mcapi.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        axes_name: str
          Name of composition axes

    Returns:

        create_sample_process: mcapi.Process instance
          The Process that created the sample
    """

    ## Create Sample
    create_sample_process = expt.create_process_from_template(
        'global_Composition Axes')
    create_sample_process.create_samples(sample_names=[axes_name])

    # "prim"
    _add_sample_measurement(create_sample_process, 'prim', prim)

    axes = casm_proj.composition_axes[axes_name]

    # end members:
    #     "origin", "a", "b", etc.
    for key, val in axes.end_members.iteritems():
        _add_vector_measurement(create_sample_process, key, val)

    # "formula"
    _add_string_measurement(create_sample_process, 'formula', axes.formula)

    # "parametric_formula"
    _add_string_measurement(
        create_sample_process,
        'parametric_formula',
        axes.param_formula)

    return create_sample_process


def create_clex_sample(expt, casm_proj, prim, clex_desc):
    """
    Create a CASM Cluster Expansion Effective Hamiltonian Sample

    Assumes expt.proj.local_abspath exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment instance

        casm_proj: casm.project.Project instance

        prim: mcapi.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        clex_desc: casm.project.ClexDescription instance

    Returns:

        create_sample_process: mcapi.Process instance
          The Process that created the sample
    """
    ## Create Sample
    create_sample_process = expt.create_process_from_template(
        'global_Cluster Expansion Effective Hamiltonian')

    # "prim" (sample)
    _add_sample_measurement(create_sample_process, 'prim', prim)

    # "bspecs" (file)
    mcfile = _add_file(expt.proj, casm_proj.dir.bspecs(clex_desc))
    _add_file_measurement(create_sample_process, 'bspecs', mcfile)

    # "eci" (file)
    mcfile = _add_file(expt.proj, casm_proj.dir.eci(clex_desc))
    _add_file_measurement(create_sample_process, 'eci', mcfile.id, mcfile.name)

    return create_sample_process
