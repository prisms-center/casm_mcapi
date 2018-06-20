"""mc casm prim subcommand"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

import sys
import casm_mcapi
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt, _trunc_name, _format_mtime
from casm.project import Project

def get_prim_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a CASM Primitive Crystal Structure sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 CASM Primitive Crystal Structure samples exist in the experiment.

    Arguments:

        expt: materials_commons.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        prim: materials_commons.Sample instance, or None
          A CASM Primitive Crystal Structure sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_prim = [proc for proc in expt.get_all_processes() if proc.template_id == casm_mcapi.templates['prim']]
        if len(candidate_prim) == 0:
            out.write('Did not find a prim sample.\n')
            out.write('Use \'mc casm prim --create\' to create a prim sample, or --prim-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_prim) > 1:
            out.write('Found multiple prim samples:')
            for cand in candidate_prim:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --prim-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        prim_proc = candidate_prim[0]
        prim_proc.decorate_with_output_samples()
        return prim_proc.output_samples[0]
    else:
        prim = expt.get_sample_by_id(sample_id)
    return prim


def create_prim_sample(expt, casm_proj, sample_name=None, verbose=False):
    """
    Create a CASM Primitive Crystal Structure Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: materials_commons.Experiment object

        casm_proj: casm.project.Project object

        sample_name: str
          Name for sample, default is: casm_proj.name + ".prim"

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: materials_commons.Process instance
          The Process that created the sample
    """
    template_id = casm_mcapi.templates['prim']

    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)
    proc.rename('Create_' + casm_proj.name + '_Prim')

    ## Create sample
    if sample_name is None:
        sample_name = casm_proj.name + ".prim"
    proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    # Sample attributes (how to check names?):
    # "name"
    proc.add_string_measurement('name', casm_proj.name)

    prim = casm_proj.prim

    # "lattice"
    #     "matrix"
    #     "parameters" (a, b, c, alpha, beta, gamma)
    #     "system" ("triclinic", "monoclinic", "orthorhombic", "tetragonal",
    #               "hexagonal", "rhombohedral", "cubic")
    #     "symmetry" (Schoenflies symbol)
    proc.add_numpy_matrix_measurement('lattice_matrix', prim.lattice_matrix)

    proc.add_vector_measurement('lattice_parameters', prim.lattice_parameters)

    proc.add_string_measurement('lattice_point_group_schonflies', prim.lattice_symmetry_s)

    proc.add_string_measurement('lattice_point_group_hermann_mauguin', prim.lattice_symmetry_hm)

    proc.add_string_measurement('lattice_system', prim.lattice_system)

    # "space_group"
    #      "point_group_schonflies"
    #      "point_group_hermann_mauguin"
    #      "number"
    #      "crystal_family" ("triclinic", "monoclinic", "orthorhombic",
    #                        "tetragonal", "hexagonal", "cubic")
    #      "crystal_system" ("triclinic", "monoclinic", "orthorhombic",
    #                        "tetragonal", "hexagonal", "trigonal", "cubic")
    proc.add_string_measurement('crystal_point_group_schonflies', prim.crystal_symmetry_s)

    proc.add_string_measurement('crystal_point_group_hermann_mauguin', prim.crystal_symmetry_hm)

    proc.add_string_measurement('crystal_family', prim.crystal_family)

    proc.add_string_measurement('crystal_system', prim.crystal_system)

    # right now, this is a string giving a range of possible values based on the
    #   crystal point group
    proc.add_string_measurement('space_group_number', prim.space_group_number)

    # "casm_prim_file"
    mcfile = expt.project.add_file_by_local_path(casm_proj.dir.prim(), verbose=verbose)
    proc.add_file_measurement('casm_prim_file', mcfile)

    # "elements" - currently only elemental components are allowed
    proc.add_list_measurement('elements', prim.elements, 'string')

    # "n_elements"
    proc.add_integer_measurement('n_elements', len(prim.elements))

    # "components" - currently only elemental components are allowed
    proc.add_list_measurement('components', prim.components, 'string')

    # "n_components"
    proc.add_integer_measurement('n_components', len(prim.components))

    # "n_independent_compositions"
    proc.add_integer_measurement('n_independent_compositions', prim.n_independent_compositions)

    # "degrees_of_freedom" ("occupation", "displacement", "strain")
    proc.add_string_measurement('degrees_of_freedom', prim.degrees_of_freedom)

    return expt.get_process_by_id(proc.id)


class PrimSubcommand(ListObjects):
    desc = "(sample) CASM Primitive Crystal Structure"

    def __init__(self):
        super(PrimSubcommand, self).__init__(["casm", "prim"], "CASM Primitive Crystal Structure", "CASM Primitive Crystal Structures",
            desc="Uploads prim.json and creates an entity (sample) representing the prim.",
            expt_member=True,
            list_columns=['name', 'owner', 'template_name', 'id', 'mtime'],
            creatable=True)

    def get_all_from_experiment(self, expt):
        return [proc for proc in expt.get_all_processes() if proc.template_id == casm_mcapi.templates[self.cmdname[-1]]]

    def get_all_from_project(self, proj):
        return [proc for proc in proj.get_all_processes() if proc.template_id == casm_mcapi.templates[self.cmdname[-1]]]

    def create(self, args, out=sys.stdout):
        proj = make_local_project()
        expt = make_local_expt(proj)
        casm_proj = Project()
        proc = create_prim_sample(expt, casm_proj, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')


    def add_create_options(self, parser):
        #some_option_help = "Some option help info"
        #parser.add_argument('--some_option', action="store_true", default=False, help=some_option_help)
        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
