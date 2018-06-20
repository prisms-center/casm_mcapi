"""mc casm config subcommand"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *

import sys
import casm_mcapi
from casm_mcapi.prim import get_prim_sample
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt, _trunc_name, _format_mtime
from casm.project import Project, Selection


def create_config_sample(expt, casm_proj, prim, configname, verbose=False):
    """
    Create a CASM Configuration Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: materials_commons.Experiment instance

        casm_proj: casm.project.Project instance

        prim: materials_commons.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        configname: str
          Configuration name

    Returns:

        proc: materials_commons.Process instance
          The Process that created the sample
    """

    ## Create Sample
    proc = expt.create_process_from_template(casm_mcapi.templates['config'])
    proc.rename(configname)
    samp = proc.create_samples(sample_names=[configname])[0]

    # "prim"
    proc.add_sample_measurement('prim', prim)

    # upload "POS" and link to sample and process
    pos_file = expt.project.add_file_by_local_path(casm_proj.dir.POS(configname), verbose=verbose)
    samp.link_files([pos_file])
    proc.add_files([pos_file])

    return expt.get_process_by_id(proc.id)


class ConfigSubcommand(ListObjects):
    desc = "(sample) CASM Configuration"

    def __init__(self):
        super(ConfigSubcommand, self).__init__(["casm", "config"], "CASM Configuration", "CASM Configurations",
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

        existing = proj.get_all_samples()

        if prim is None:
            return
        if args.confignames is not None:
            for configname in args.confignames:
                self._create_one(args, expt, casm_proj, prim, configname, existing, out)
        if args.selection is not None:
            print(args.selection)
            sel = Selection(casm_proj, args.selection[0], all=False)
            for configname in sel.data['configname']:
                self._create_one(args, expt, casm_proj, prim, configname, existing, out)

    def _create_one(self, args, expt, casm_proj, prim, configname, existing, out):
        if not args.force:
            matches = [samp for samp in existing if samp.name == configname]
            if len(matches):
                out.write('Found existing sample for configuration ' + configname + '.  Skipping.\n')
                return
        proc = create_config_sample(expt, casm_proj, prim, configname, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')

    def add_create_options(self, parser):
        prim_id_help = "Specify prim sample id explicitly"
        parser.add_argument('--prim-id', nargs='*', default=None, help=prim_id_help)

        confignames_help = "Specify config names explicitly"
        parser.add_argument('--confignames', nargs='*', default=None, help=confignames_help)

        selection_help = "Specify a CASM selection of configurations"
        parser.add_argument('--selection', nargs=1, default=None, help=selection_help)
        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
