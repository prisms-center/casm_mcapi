"""CASM - Materials Commons interface"""

from casm_mcapi.main import casm_subcommand

def set_templates(value=None):
    """
    Enable swapping out templates
    """
    global templates

    if value is None:
        # dictionary of cmdname -> template_id
        templates = {
          'dft': 'global_Density Functional Theory Calculation',
          'clex': 'global_CASM Cluster Expansion Effective Hamiltonian',
          'comp': 'global_CASM Composition Axes',
          'config': 'global_CASM Configuration',
          'fit': 'global_CASM ECI Fitting Procedure',
          'monte': 'global_CASM Monte Carlo Calculation',
          'prim': 'global_CASM Primitive Crystal Structure',
        }
    else:
        templates = value

# set default template ids
set_templates()

# specify the version of casm these functions work for
CASM_VERSION = "0.3.X"
MCAPI_NAME = "casm"
MCAPI_DESC = "Create and inspect CASM samples, processes, measurements, etc."
MCAPI_MODULE = "casm_mcapi"
MCAPI_SUBCOMMAND = "casm_subcommand"

__all__ = [
    'MCAPI_NAME',
    'MCAPI_DESC',
    'casm_subcommand',
    'set_templates']
