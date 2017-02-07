"""CASM - Materials Commons CLI"""

import argparse
import sys

MCAPI_NAME = "casm"
MCAPI_DESC = "Create CASM samples, processes, measurements, etc."

def casm_subcommand():
    """
    Specialized CASM commands for the Materials Commons CLI
    """

    prim_help = "Upload CASM Primitive Crystal Structure sample"
    composition_help = "Upload CASM Composition Axes sample"
    clex_help = "Upload CASM Cluster Expansion sample"
    mc_help = "Upload CASM Monte Carlo process"

    parser = argparse.ArgumentParser(description=MCAPI_DESC)
    parser.add_argument('--prim', help=prim_help, action="store_true", default=False)
    parser.add_argument('--composition', help=composition_help, action="store_true", default=False)
    parser.add_argument('--clex', help=clex_help, action="store_true", default=False)
    parser.add_argument('--mc', help=mc_help, action="store_true", default=False)

    # ignore 'mc casm'
    args = parser.parse_args(sys.argv[2:])

    print "mc casm ...do something..."
