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
import dump
import printer
import semantics
import translate
import tables
import build

# Constants
DEFAULT_TRANSLATION_FILE = 'program.xc'
DEFAULT_INPUT_FILE       = 'stdin'
DEFAULT_OUTPUT_FILE      = 'a.out'
PARSE_LOG_FILE           = 'parselog.txt'
DEFAULT_NUM_CORES        = 4

# Globals
verbose = False

def setup_argparse():
    """ Configure an argument parser object 
    """
    p = argparse.ArgumentParser(description='sire compiler')
    p.add_argument('infile', metavar='<input-file>', default=DEFAULT_INPUT_FILE,
            help='specify the input filename')
    p.add_argument('-o', nargs=1, metavar='<file>', 
            dest='outfile', default=DEFAULT_OUTPUT_FILE,
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

def translate_ast(program, sem, program_buf, jumptab_buf, sizetab_buf):
    """ Transform an AST into XC 
    """
    verbose_msg("Translating AST\n")

    # Translate the AST
    walker = translate.Translate(semantics, program_buf)
    walker.walk_program(program)

    # Output the jump table
    tables.build_jumptab(jumptab_buf, sem.proc_names)

    # Output the size table
    tables.build_sizetab(sizetab_buf, sem.proc_names)

def build_(program_buf, jumptab_buf, sizetab_buf, numcores, compile_only):
    """ Build the program executable 
    """
    verbose_msg("Building executable\n")
    builder = build.Build(numcores, verbose=True)
    if compile_only:
        builder.compile(program_buf)
    else:
        builder.run(program_buf, jumptab_buf, sizetab_buf)

def verbose_msg(msg):
    if verbose: 
        sys.stdout.write(msg)
        sys.stdout.flush()

def main(args):
        
    # Setup parser and parse arguments
    argp = setup_argparse()
    a = argp.parse_args(args)
    global verbose
    verbose = a.verbose

    # Setup the error object
    err = error.Error()

    # Read the input file 
    input = util.read_file(a.infile)
    if not input:
        return

    # Parse the input file
    program = parse(input, a.infile, err)
    if a.parse_only:
        return

    # Perform semantic analysis
    sem = semantic_analysis(program, err)
    if a.sem_only:
        return

    # Display (dump) the AST
    if a.show_ast:    
        program.accept(dump.Dump())
        return

    # Display (pretty-print) the AST
    if a.pprint: 
        walker.walk_program(printer.Printer())
        return
   
    # Translate the AST
    program_buf = io.StringIO()
    jumptab_buf = io.StringIO()
    sizetab_buf = io.StringIO()
    translate_ast(program, sem, program_buf, jumptab_buf, sizetab_buf)
    if a.translate_only:
        util.write_file(DEFAULT_TRANSLATION_FILE, program_buf.getvalue())
        return

    # Compile, assemble and link with the runtime
    build_(program_buf, jumptab_buf, sizetab_buf, a.numcores, a.compile_only)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
   
