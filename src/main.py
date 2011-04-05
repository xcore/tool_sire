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

import common.error as error
import common.util as util
import common.config as config
import common.definitions as defs

from parser.parser import Parser
import parser.dump
import parser.printer

import analysis.semantics
import analysis.children

import codegen.target.xs1.device as device
import codegen.target.xs1.translate as translate
import codegen.target.xs1.build as build

# Constants
SUCCESS                  = 0
FAILURE                  = 1
DEFINITIONS_FILE         = 'definitions.h'
DEFAULT_TRANSLATION_FILE = 'program.xc'
DEFAULT_OUTPUT_XC        = 'a.xc'
DEFAULT_OUTPUT_S         = 'a.S'
DEFAULT_OUTPUT_XE        = 'a.xe'
PARSE_LOG_FILE           = 'parselog.txt'
DEFAULT_NUM_CORES        = 1

# Globals
verbose = False
proceede = True

def setup_argparse():
    """ Configure an argument parser object 
    """
    p = argparse.ArgumentParser(description='sire compiler', prog='sire')
    
    p.add_argument('infile', nargs='?', metavar='<input-file>', 
            default=None,
            help='input filename')
    
    p.add_argument('-o', nargs=1, metavar='<file>', 
            dest='outfile', default=None,
            help='output filename')
    
    p.add_argument('-n', '--numcores', nargs=1, metavar='<n>', 
            dest='num_cores', default=[DEFAULT_NUM_CORES],
            help='number of cores')
    
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
            help='display status messages')
    
    p.add_argument('-e', '--display-calls', action='store_true',
            dest='show_calls', help='display external commands invoked ')
    
    p.add_argument('-r', '--parse', action='store_true', dest='parse_only', 
            help='parse the input file and quit')

    p.add_argument('-s', '--sem', action='store_true', dest='sem_only', 
            help='perform semantic analysis and quit')
    
    p.add_argument('-a', '--display-ast', action='store_true', dest='show_ast',
            help='display the AST and quit')
    
    p.add_argument('-p', '--pprint-ast', action='store_true', dest='pprint',
            help='pretty-print the AST and quit')
    
    p.add_argument('-t', '--translate', action='store_true',
            dest='translate_only',
            help='translate but do not compile')
    
    p.add_argument('-c', '--compile', action='store_true',
            dest='compile_only',
            help='compile but do not assemble and link')
    
    p.add_argument('-d', '--devices', action='store_true',
            dest='display_devices',
            help='display available devices')
    
    return p

def setup_globals(a):
    """ Setup global variables for this module to control execution of
        compilation
    """
    
    global verbose
    global display_devices
    global show_calls
    global num_cores
    global infile
    global outfile
    global parse_only
    global sem_only
    global show_ast
    global pprint
    global translate_only
    
    verbose         = a.verbose
    display_devices = a.display_devices
    show_calls      = a.show_calls
    num_cores       = int(a.num_cores[0])
    infile          = a.infile
    parse_only      = a.parse_only
    sem_only        = a.sem_only
    compile_only    = a.compile_only
    show_ast        = a.show_ast
    pprint          = a.pprint
    translate_only  = a.translate_only

    if not a.outfile:
        if translate_only: outfile = DEFAULT_OUTPUT_XC 
        elif compile_only: outfile = DEFAULT_OUTPUT_S
        else:              outfile = DEFAULT_OUTPUT_XE
    else:
        outfile = a.outfile[0]

def set_device(num_cores):
    """ Check num_cores is valid for an available device """
    #d = AVAILABLE_DEVICES.find(lambda x: num_cores==x.num_cores())
    d = [x for x in device.AVAILABLE_DEVICES if num_cores == x.num_cores()]
    if d:
        return d[0]
    else:
        sys.stderr.write('Invalid number of cores ({}), valid devices:\n'.format(
            num_cores))
        for x in device.AVAILABLE_DEVICES:
            sys.stderr.write('  {}\n'.format(x.name))
        return None

def show_devices():
    print('Available devices:')
    [print('  '+x.name) for x in device.AVAILABLE_DEVICES]

def parse(logging=False):
    """ Parse an input string to produce an AST 
    """
    global ast
    verbose_msg("Parsing file '{}'\n".format(infile if infile else 'stdin'))
    if logging:
        logging.basicConfig(
            level = logging.DEBUG,
            filename = PARSE_LOG_FILE,
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s")
        log = logging.getLogger()
    else:
        log = 0
    parser = Parser(err, lex_optimise=True, 
            yacc_debug=False, yacc_optimise=False)
    ast = parser.parse(input, infile, debug=log)

def semantic_analysis():
    """ Perform semantic analysis on an AST 
    """
    global sem
    verbose_msg("Performing semantic analysis\n")
    sem = semantics.Semantics(err)
    ast.accept(sem)

def child_analysis():
    """ Determine children
    """
    global child
    verbose_msg("Performing child analysis\n")
    child = children.Children(sem.proc_names)
    ast.accept(child)
    child.build()
    #child.display()

def translate_ast():
    """ Transform an AST into XC 
    """
    global translate_buf
    verbose_msg("Translating AST\n")
    translate_buf = io.StringIO()
    walker = translate.Translate(sem, child, translate_buf)
    walker.walk_program(ast)
    if translate_only:
        util.write_file(outfile, translate_buf.getvalue())

def builder(outfile, compile_only):
    """ Build the program executable 
    """
    global proceede
    verbose_msg('[Building an executable for {} cores]\n'.format(
            num_cores))
    builder = build.Build(num_cores, sem, verbose, show_calls)
    if compile_only:
        proceede = builder.compile_only(translate_buf, outfile, device)
    else:
        proceede = builder.run(translate_buf, outfile, device)

def verbose_msg(msg):
    if verbose: 
        sys.stdout.write(msg)
        sys.stdout.flush()

# TODO: Ensure proper error handling for each stage here

def main(args):
    
    global proceede
    global err
    global ast
    global input
    global translate_buf
    global sem
    global child
    global device

    # Setup the error object
    err = error.Error()

    # Setup the configuration variables
    proceede = config.init(err)
    if not proceede:
        return FAILURE

    # Load definitions
    proceede = defs.load(config.INCLUDE_PATH+'/'+DEFINITIONS_FILE)
    if not proceede:
        return FAILURE

    # Setup parser, parse arguments and initialise globals
    argp = setup_argparse()
    a = argp.parse_args(args)
    setup_globals(a)

    # Display devices
    if display_devices:
        show_devices()
        return SUCCESS

    # Set the device
    device = set_device(num_cores)
    if not device:
        return FAILURE
    
    # Read the input from stdin or from a file 
    input = util.read_file(infile) if infile else sys.stdin.read()
    if not input: 
        return FAILURE

    # Parse the input file and produce an AST
    parse()
    if err.any(): 
        return FAILURE
    if parse_only: 
        return SUCCESS

    # Perform semantic analysis on the AST
    semantic_analysis()
    if err.any(): 
        return FAILURE
    if sem_only: 
        return SUCCESS

    # Perform child analysis
    child_analysis()

    # Display (dump) the AST
    if show_ast:
        ast.accept(dump.Dump())
        return SUCCESS

    # Display (pretty-print) the AST
    if pprint: 
        walker = printer.Printer()
        walker.walk_program(ast)
        return SUCCESS
   
    # Translate the AST
    translate_ast()
    if translate_only:
        return SUCCESS

    # Compile, assemble and link with the runtime
    builder(outfile, a.compile_only)
    if not proceede:
        return FAILURE

    verbose_msg('Produced file: '+outfile+'\n')
    
    return SUCCESS

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
   
