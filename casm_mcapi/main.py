"""CASM - Materials Commons CLI"""

import argparse
import sys
import StringIO
from casm_mcapi.clex import ClexSubcommand
from casm_mcapi.comp import CompSubcommand
from casm_mcapi.config import ConfigSubcommand
from casm_mcapi.dft import DFTSubcommand
from casm_mcapi.fit import FitSubcommand
from casm_mcapi.monte import MonteSubcommand
from casm_mcapi.prim import PrimSubcommand

import casm_mcapi.samples

casm_usage = [
    {'name':'prim', 'desc': PrimSubcommand.desc, 'subcommand': PrimSubcommand()},
    {'name':'comp', 'desc': CompSubcommand.desc, 'subcommand': CompSubcommand()},
    {'name':'clex', 'desc': ClexSubcommand.desc, 'subcommand': ClexSubcommand()},
    {'name':'config', 'desc': ConfigSubcommand.desc, 'subcommand': ConfigSubcommand()},
    {'name':'dft', 'desc': DFTSubcommand.desc, 'subcommand': DFTSubcommand()},
    {'name':'fit', 'desc': FitSubcommand.desc, 'subcommand': FitSubcommand()},
    {'name':'monte', 'desc': MonteSubcommand.desc, 'subcommand': MonteSubcommand()}
]

def casm_subcommand(argv=sys.argv):
    usage_help = StringIO.StringIO()
    usage_help.write("mc casm <command> [<args>]\n\n")
    usage_help.write("The mc casm commands are:\n")
    
    for interface in casm_usage:
        usage_help.write("  {:20} {:40}\n".format(interface['name'], interface['desc']))
    interfaces = {d['name']: d for d in casm_usage}
    
    parser = argparse.ArgumentParser(
        description='Materials Commons - CASM command line interface',
        usage=usage_help.getvalue())
    parser.add_argument('command', help='Subcommand to run')
    
    if len(argv) < 3:
        parser.print_help()
        return
    
    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = parser.parse_args(argv[2:3])
    
    if args.command in interfaces:
        interfaces[args.command]['subcommand'](argv)
    else:
        print 'Unrecognized command'
        parser.print_help()
        exit(1)


