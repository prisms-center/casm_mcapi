"""CASM - Materials Commons CLI"""

import argparse
import sys
import casm.project
import mcapi.misc
import casm_mcapi.samples

MCAPI_NAME = "casm"
MCAPI_DESC = "Create CASM samples, processes, measurements, etc."

def casm_subcommand():
    """
    Specialized CASM commands for the Materials Commons CLI
    """

    prim_help = "Create CASM Primitive Crystal Structure sample"
    composition_help = "Create CASM Composition Axes sample"
    clex_help = "Create CASM Cluster Expansion sample"
    mc_help = "Create CASM Monte Carlo process"

    parser = argparse.ArgumentParser(description=MCAPI_DESC)
    parser.add_argument('--prim', help=prim_help, action="store_true", default=False)
    parser.add_argument('--composition', help=composition_help, action="store_true", default=False)
    parser.add_argument('--clex', help=clex_help, action="store_true", default=False)
    parser.add_argument('--mc', help=mc_help, action="store_true", default=False)

    # ignore 'mc casm'
    args = parser.parse_args(sys.argv[2:])

    mc_proj = mcapi.misc.make_local_project()
    mc_expt = mcapi.misc.make_local_expt(mc_proj)
    if mc_expt is None:
        print "no experiment set, use 'mc expt' to create or set the current expt"
        exit(1)

    if args.prim:
        print "Create CASM project... "
        casm_proj = casm.project.Project()

        print "Create prim sample... "
        proc = casm_mcapi.samples.create_prim_sample(mc_expt, casm_proj)
        print "DONE\n"

        print "Process:"
        for key, val in proc.__dict__.iteritems():
            print key + ":", val


    elif args.composition:
        print "Create composition axes sample"

    elif args.clex:
        print "Create cluster expansion sample"

    elif args.mc:
        print "Create Monte Carlo process"

    else:
        print "No command recognized"
        parser.print_help()
