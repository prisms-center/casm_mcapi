"""mc casm monte subcommand"""

import casm_mcapi
from mcapi.cli import ListObjects

class MonteSubcommand(ListObjects):
    desc = "(process) CASM Monte Carlo Calculations"
    
    def __init__(self):
        super(MonteSubcommand, self).__init__(["casm", "monte"], "CASM Monte Carlo Calculation", "CASM Monte Carlo Calculations", 
            expt_member=True, list_columns=['name', 'owner', 'template_name', 'id', 'mtime'],
            creatable=True)
    
    def get_all_from_experiment(self, expt):
        return [proc for proc in expt.get_all_processes() if proc.template_id == casm_mcapi.templates[self.cmdname[-1]]]
    
    def get_all_from_project(self, proj):
        return [proc for proc in proj.get_all_processes() if proc.template_id == casm_mcapi.templates[self.cmdname[-1]]]
    
    def create(self, args):
        print "create a '" + casm_mcapi.templates[self.cmdname[-1]] + "' is not yet implemented"
        return
    
    def add_create_options(self, parser):
        some_option_help = "Some option help info"
        parser.add_argument('--some_option', action="store_true", default=False, help=some_option_help)
        return
    
    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
