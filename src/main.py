#! /usr/bin/env python3

# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import io
import os
import argparse
import logging

from error import Error
from errorlog import ErrorLog
from util import vmsg
from util import vhdr
import util
import config
import definitions as defs
from parser import Parser
import dump as dump
import printer as printer
import semantics as semantics
import children as children

from codegen import generate
from target.config import set_device
from target.config import TARGET_SYSTEMS
from target.config import DEFAULT_NUM_CORES
from target.config import DEFAULT_TARGET_SYSTEM

# Globals
v = False

def setup_argparse():
    """ Configure an argument parser object 
    """
    p = argparse.ArgumentParser(description=
            'sire compiler v'+defs.VERSION, prog='sire')
    
    # Input/output targets

    p.add_argument('infile', nargs='?', metavar='<input-file>', default=None,
            help='input filename')
    
    p.add_argument('-o', nargs=1, metavar='<file>', 
            dest='outfile', default=None,
            help="output filename (default: '"+defs.DEFAULT_OUT_FILE+".*')")
   
    # System parameters

    p.add_argument('-t', nargs=1, choices=TARGET_SYSTEMS, 
            dest='target_system', default=[DEFAULT_TARGET_SYSTEM],
            help='target system (default: '+DEFAULT_TARGET_SYSTEM+')')
    
    p.add_argument('-n', nargs=1, metavar='<n>', type=int, 
            dest='num_cores', default=[DEFAULT_NUM_CORES],
            help='number of cores (default: {})'.format(DEFAULT_NUM_CORES))
    
    # Verbosity

    p.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
            help='display status messages')
    
    p.add_argument('-c', '--display-calls', action='store_true',
            dest='show_calls', help='display external commands invoked ')
    
    # Stages

    p.add_argument('-r', '--parse', action='store_true', dest='parse_only', 
            help='parse the input file and quit')

    p.add_argument('-s', '--sem', action='store_true', dest='sem_only', 
            help='perform semantic analysis and quit')
    
    p.add_argument('-p', '--print-ast', action='store_true', dest='print_ast',
            help='display the AST and quit')
        
    p.add_argument('-P', '--pprint-ast', action='store_true', dest='pprint_ast',
            help='pretty-print the AST and quit')
    
    p.add_argument('-T', '--translate', action='store_true',
            dest='translate_only',
            help='translate but do not compile')
    
    p.add_argument('-C', '--compile', action='store_true',
            dest='compile_only',
            help='compile but do not assemble and link')
    
    return p

def setup_globals(a):
    """ Setup global variables representing compilation parameters
    """
   
    # Verbosity
    global v
    global show_calls
    v = a.verbose
    show_calls = a.show_calls
    
    # System paramters
    global target_system
    global num_cores
    target_system = a.target_system[0]
    num_cores = int(a.num_cores[0])

    # Stages
    global print_ast
    global pprint_ast
    global parse_only
    global sem_only
    global translate_only
    global compile_only
    parse_only = a.parse_only
    sem_only = a.sem_only
    compile_only = a.compile_only
    print_ast = a.print_ast
    pprint_ast = a.pprint_ast
    translate_only = a.translate_only
    compile_only = a.compile_only

    # Input/output targets
    global infile
    global outfile
    infile = a.infile
    outfile = a.outfile[0] if a.outfile else defs.DEFAULT_OUT_FILE

def produce_ast(input_file, errorlog, logging=False):
    """ Parse an input string to produce an AST 
    """
    vmsg(v, "Parsing file '{}'".format(infile if infile else 'stdin'))
   
    # Setup logging if we need to
    if logging:
        logging.basicConfig(
            level = logging.DEBUG,
            filename = defs.PARSE_LOG_FILE,
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s")
        log = logging.getLogger()
    else:
        log = 0
   
    # Create the parser and produce the AST
    parser = Parser(errorlog, lex_optimise=True, 
            yacc_debug=False, yacc_optimise=False)
    ast = parser.parse(input_file, infile, debug=log)
    
    if errorlog.any():
        raise Error('parsing')
    
    # Perform parsing only
    if parse_only: 
        raise SystemExit()
    
    # Display (dump) the AST
    if print_ast:
        ast.accept(dump.Dump())
        raise SystemExit()

    # Display (pretty-print) the AST
    if pprint_ast: 
        printer.Printer().walk_program(ast)
        raise SystemExit()

    return ast

def semantic_analysis(ast, errorlog):
    """ Perform semantic analysis on an AST 
    """
    vmsg(v, "Performing semantic analysis")
    
    sem = semantics.Semantics(errorlog)
    ast.accept(sem)
    
    if errorlog.any():
        raise Error('semantic analysis')
    
    if sem_only: 
        raise SystemExit()
    
    return sem

def child_analysis(ast, sem):
    """ Determine children
    """
    vmsg(v, "Performing child analysis")
    
    child = children.Children(sem.proc_names)
    ast.accept(child)
    child.build()
    #child.display()
    
    return child

def main(args):
    
    try:

        # Setup the configuration variables and definitions
        config.init()

        # Setup parser, parse arguments and initialise globals
        argp = setup_argparse()
        a = argp.parse_args(args)
        setup_globals(a)

        # Create a (valid) target system device oject (before anything else)
        device = set_device(target_system, num_cores)
        
        # Read the input from stdin or from a file 
        vhdr(v, 'Front end')
        input_file = util.read_file(infile) if infile else sys.stdin.read()

        # Setup the error object
        errorlog = ErrorLog()
        
        # Parse the input file and produce an AST
        ast = produce_ast(input_file, errorlog)

        # Perform semantic analysis on the AST
        sem = semantic_analysis(ast, errorlog)

        # Perform child analysis
        child = child_analysis(ast, sem)

        # Generate code
        vhdr(v, 'Generating code for {}'.format(device))
        generate(ast, sem, child, device, outfile, 
                translate_only, compile_only, show_calls, v)

    # Handle any specific compilation errors
    except Error as e:
        sys.stderr.write('Error: {}\n'.format(e))
        return 1
    
    # Handle system exits
    except SystemExit:
        return 0
  
    # Anything else we weren't expecting
    except:
        sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
        raise
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
   
