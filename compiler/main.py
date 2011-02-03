#! /usr/bin/env python3.1

import sys
import io
import os
import argparse

from ply import *
from parser import Parser
import logging

import error
import util
import definitions
import config
import dump
import printer
import semantics
import children
import translate
import build

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
            dest='numcores', default=[DEFAULT_NUM_CORES],
            help='number of cores')
    
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
            help='display status messages')
    
    p.add_argument('-e', '--display-calls', action='store_true',
            dest='showcalls', help='display external commands invoked ')
    
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
    
    return p

def setup_globals(a):
    """ Setup global variables for this module to control execution of
        compilation
    """
    
    global verbose
    global showcalls
    global numcores
    global infile
    global outfile
    global parse_only
    global sem_only
    global show_ast
    global pprint
    global translate_only
    
    verbose        = a.verbose
    showcalls      = a.showcalls
    numcores       = int(a.numcores[0])
    infile         = a.infile
    parse_only     = a.parse_only
    sem_only       = a.sem_only
    compile_only   = a.compile_only
    show_ast       = a.show_ast
    pprint         = a.pprint
    translate_only = a.translate_only

    if not a.outfile:
        if translate_only: outfile = DEFAULT_OUTPUT_XC 
        elif compile_only: outfile = DEFAULT_OUTPUT_S
        else:              outfile = DEFAULT_OUTPUT_XE
    else:
        outfile = a.outfile[0]

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
            numcores))
    builder = build.Build(numcores, sem, verbose, showcalls)
    if compile_only:
        proceede = builder.compile_only(translate_buf, outfile)
    else:
        proceede = builder.run(translate_buf, outfile)

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

    # Setup the error object
    err = error.Error()

    # Setup the configuration variables
    proceede = config.init(err)
    if not proceede:
        return FAILURE

    # Load definitions
    proceede = definitions.load(config.INCLUDE_PATH+'/'+DEFINITIONS_FILE)
    if not proceede:
        return FAILURE

    # Setup parser, parse arguments and initialise globals
    argp = setup_argparse()
    a = argp.parse_args(args)
    setup_globals(a)

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
        walker.walk_program(printer.Printer())
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
   
