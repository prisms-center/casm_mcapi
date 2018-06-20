"""mc casm config subcommand"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

import sys
import casm_mcapi
from casm_mcapi.prim import get_prim_sample
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt, _trunc_name, _format_mtime
from casm.project import Project

def create_composition_axes_sample(expt, casm_proj, prim, axes_name=None, verbose=False):
    """
    Create a CASM Composition Axes Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: materials_commons.Experiment instance

        casm_proj: casm.project.Project instance

        prim: materials_commons.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        axes_name: str, optional (default=None uses current axes)
          Name of composition axes

    Returns:

        proc: materials_commons.Process instance
          The Process that created the sample
    """
    if axes_name is None:
        axes = casm_proj.composition_axes
        axes_name = axes.name
    else:
        axes = casm_proj.all_composition_axes[axes_name]

    ## Create Sample
    proc = expt.create_process_from_template(casm_mcapi.templates['comp'])
    proc.create_samples(sample_names=['Composition_Axes_' + axes_name])

    # "prim"
    proc.add_sample_measurement('prim', prim)

    # end members:
    #     "origin", "a", "b", etc.
    for key, val in axes.end_members.iteritems():
        proc.add_vector_measurement('end_members_' + key, val.tolist())

    # "mol_formula"
    proc.add_string_measurement('mol_formula', axes.mol_formula)

    # "parametric_formula"
    proc.add_string_measurement('parametric_formula', axes.param_formula)

    return expt.get_process_by_id(proc.id)


class CompSubcommand(ListObjects):
    desc = "(sample) CASM Composition Axes"

    def __init__(self):
        super(CompSubcommand, self).__init__(["casm", "comp"], "CASM Composition Axes", "CASM Composition Axes",
            desc="Uploads composition_axes.json file and and creates an entity (sample) representing the currently chosen composition axes.",
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
        prim = get_prim_sample(expt, sample_id=args.prim_id, out=out)
        if prim is None:
            return
        proc = create_composition_axes_sample(expt, casm_proj, prim, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')

    def add_create_options(self, parser):
        prim_id_help = "Specify prim sample id explicitly"
        parser.add_argument('--prim-id', nargs='*', default=None, help=prim_id_help)
        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
