"""mc casm dft subcommand"""

import sys
import casm_mcapi
from casm_mcapi.prim import get_prim_sample
from mcapi.cli import ListObjects
from mcapi.cli.functions import make_local_project, make_local_expt
from casm.project import Project, Selection

def _set_property_set_id(s):
    if s.property_set_id is None:
        for proc in s.input_data['processes']:
            if proc['category'] == 'create_sample' and proc['direction'] == 'out':
                s.property_set_id = proc['property_set_id']
                break

def create_dft_calculation(expt, casm_proj, prim, config_sample, verbose=False):
    """
    Create a Density Functional Theory Configuration Process for default calctype
    and specified configuration and upload files.

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment instance

        casm_proj: casm.project.Project instance

        prim: mcapi.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        config_sample: mcapi.Sample instance 
          The Configuration sample that was calculated

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    
    ## Create Process
    calcname = config_sample.name + '/calctype.' + casm_proj.settings.default_clex.calctype
    proc = expt.create_process_from_template(casm_mcapi.templates['dft'])
    proc.rename(calcname)
    
    # Add input sample (set property_set_id hack)
    input_samples = [prim, config_sample]
    for s in input_samples:
        _set_property_set_id(s)
    proc.add_input_samples_to_process(input_samples)
    
    # upload files and link to process
    calcdir = casm_proj.dir.calctype_dir(config_sample.name, casm_proj.settings.default_clex)
    file_list, error = expt.project.add_directory_tree_by_local_path(calcdir, verbose=verbose)
    proc.add_files(file_list)
    
    return expt.get_process_by_id(proc.id)


class DFTSubcommand(ListObjects):
    desc = "(process) CASM Density Functional Theory Calculation"
    
    def __init__(self):
        super(DFTSubcommand, self).__init__(["casm", "dft"], "CASM Density Functional Theory Calculation", "CASM Density Functional Theory Calculations", 
            desc="Uploads calculation files for the current calctype and and creates processes representing the calculations.",
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
        
        existing_samp = expt.get_all_samples()
        existing_proc = expt.get_all_processes()
        
        if prim is None:
            return
        if args.confignames is not None:
            for configname in args.confignames:
                self._create_one(args, expt, casm_proj, prim, configname, existing_samp, existing_proc, out)
        if args.selection is not None:
            print args.selection
            sel = Selection(casm_proj, args.selection[0], all=False)
            for configname in sel.data['configname']:
                self._create_one(args, expt, casm_proj, prim, configname, existing_samp, existing_proc, out)

    def _create_one(self, args, expt, casm_proj, prim, configname, existing_samp, existing_proc, out):
        if not args.force:
            matches = [samp for samp in existing_samp if samp.name == configname]
            if len(matches) == 0:
                out.write('Did not find existing sample for configuration ' + configname + '.  Skipping.\n')
                return
            if len(matches) > 1:
                out.write('Find multiple existing sample for configuration ' + configname + '.  Skipping.\n')
                return
            config_sample = matches[0]
            calcname = configname + '/calctype.' + casm_proj.settings.default_clex.calctype
            matches = [proc for proc in existing_proc if proc.name == calcname]
            if len(matches):
                out.write('Found existing calculation for configuration ' + configname + '.  Skipping.\n')
                return
        proc = create_dft_calculation(expt, casm_proj, prim, config_sample, verbose=True)
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
