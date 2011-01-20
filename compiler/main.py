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
import translate
import build

# Constants
SUCCESS                  = 0
FAILURE                  = 1
DEFINITIONS_FILE         = 'definitions.h'
DEFAULT_TRANSLATION_FILE = 'program.xc'
DEFAULT_INPUT_FILE       = 'stdin'
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
    p = argparse.ArgumentParser(description='sire compiler')
    p.add_argument('infile', metavar='<input-file>', default=DEFAULT_INPUT_FILE,
            help='specify the input filename')
    p.add_argument('-o', nargs=1, metavar='<file>', 
            dest='outfile', default=None,
            help='specify the output filename')
    p.add_argument('-n', '--numcores', nargs=1, metavar='<n>', 
            dest='numcores', default=DEFAULT_NUM_CORES,
            help='specify the output filename')
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
            help='display status messages')
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

def parse(input, filename, error, logging=False):
    """ Parse an input string to produce an AST 
    """
    verbose_msg("Parsing file '{}'\n".format(filename))
    if logging:
        logging.basicConfig(
            level = logging.DEBUG,
            filename = PARSE_LOG_FILE,
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s")
        log = logging.getLogger()
    else:
        log = 0
    parser = Parser(error, lex_optimise=True, 
            yacc_debug=False, yacc_optimise=False)
    program = parser.parse(input, filename, debug=log)
    return program

def semantic_analysis(program, error):
    """ Perform semantic analysis on an AST 
    """
    verbose_msg("Performing semantic analysis\n")
    visitor = semantics.Semantics(error)
    program.accept(visitor)
    return visitor

def translate_ast(program, sem, buf):
    """ Transform an AST into XC 
    """
    verbose_msg("Translating AST\n")

    # Translate the AST
    walker = translate.Translate(sem, buf)
    walker.walk_program(program)

def build_(sem, buf, numcores, outfile, compile_only):
    """ Build the program executable 
    """
    verbose_msg("Building executable\n")
    builder = build.Build(numcores, sem, verbose)
    if compile_only:
        return builder.compile(buf, outfile)
    else:
        return builder.run(buf, outfile)

def verbose_msg(msg):
    if verbose: 
        sys.stdout.write(msg)
        sys.stdout.flush()

# TODO: Ensure proper error handling for each stage here

def main(args):
    
    global proceede
    global verbose

    # Setup the error object
    err = error.Error()

    # Setup the configuration variables
    proceede = config.init(err)
    if not proceede: return FAILURE

    # Load definitions
    proceede = definitions.load(config.INCLUDE_PATH+'/'+DEFINITIONS_FILE)
    if not proceede: return FAILURE

    # Setup parser and parse arguments
    argp = setup_argparse()
    a = argp.parse_args(args)
    verbose = a.verbose

    # Read the input file 
    input = util.read_file(a.infile)
    if not input: return FAILURE

    # Parse the input file
    program = parse(input, a.infile, err)
    if err.any(): return FAILURE
    if a.parse_only: return SUCCESS

    # Perform semantic analysis
    sem = semantic_analysis(program, err)
    if err.any(): return FAILURE
    if a.sem_only: return SUCCESS

    # Display (dump) the AST
    if a.show_ast:    
        program.accept(dump.Dump())
        return SUCCESS

    # Display (pretty-print) the AST
    if a.pprint: 
        walker.walk_program(printer.Printer())
        return SUCCESS
   
    # Translate the AST
    buf = io.StringIO()
    translate_ast(program, sem, buf)
    if a.translate_only:
        if not a.outfile:
            outfile = DEFAULT_OUTPUT_XC
        util.write_file(outfile, buf.getvalue())
        return SUCCESS

    # Compile, assemble and link with the runtime
    if not a.outfile:
        if a.compile_only: outfile = DEFAULT_OUTPUT_S
        else: outfile = DEFAULT_OUTPUT_XE
    else:
        outfile = a.outfile[0]
    proceede = build_(sem, buf, a.numcores, outfile, a.compile_only)
    if not proceede:
        return FAILURE

    return SUCCESS

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
   
