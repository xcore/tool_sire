#!/usr/bin/env python3.1

import sys
import argparse
from ply import *
from parser import Parser
import semantics
import printer
import translate
import dump
import logging
import error
import io
import os

DEFAULT_TRANSLATION_FILE = 'a.xc'
DEFAULT_INPUT_FILE = 'stdin'
DEFAULT_OUTPUT_FILE = 'a.out'
verbose = False

def setup_argparse():
    """ Configure an argument parser object """
    p = argparse.ArgumentParser(description='sire compiler')
    p.add_argument('infile', metavar='<input-file>', default=DEFAULT_INPUT_FILE,
            help='specify the input filename')
    p.add_argument('-o', nargs=1, metavar='<file>', dest='outfile',
            default=DEFAULT_OUTPUT_FILE,
            help='specify the output filename')
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose', 
            help='display status messages')
    p.add_argument('-s', '--sem', action='store_true', dest='sem_only', 
            help='perform semantic analysis and quit')
    p.add_argument('-a', '--ast', action='store_true', dest='show_ast',
            help='display the AST and quit')
    p.add_argument('-p', '--pprint', action='store_true', dest='pprint',
            help='pretty-print the AST and quit')
    p.add_argument('-t', '--translate', action='store_true',
            dest='translate_only',
            help='translate but do not compile')
    p.add_argument('-c', '--compile', action='store_true',
            dest='compile_only',
            help='compile but do not assemble and link')
    return p

def read_input(filename):
    """ Read a file and return its contents as a string """
    verbose_report("Reading input file '{}'...".format(filename))
    try:
        file = open(filename, 'r')
        contents = file.read()
        file.close()
    except(IOError, (errno, stderror)):
        print('I/O error({}): {}'.format(errno, stderror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])
    verbose_report("done.\n")
    return contents

def write_output(buf, filename):
    """ Write the output to a file """
    verbose_report("Writing output file '{}'...".format(filename))
    try:
        file = open(filename, 'w')
        file.write(buf.getvalue())
        file.close()
    except IOError as err:
        print('I/O error({}): {}'.format(err.errno, err.stderror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])
    verbose_report("done.\n")

def parse(input, filename, error, logging=False):
    """ Parse an input string to produce an AST """
    verbose_report("Parsing file '{}'...".format(filename))
    if logging:
        logging.basicConfig(
            level = logging.DEBUG,
            filename = "parselog.txt",
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s")
        log = logging.getLogger()
    else:
        log = 0
    parser = Parser(error, lex_optimise=True, 
            yacc_debug=False, yacc_optimise=False)
    program = parser.parse(input, filename, debug=log)
    verbose_report("done.\n")
    return program

def semantic_analysis(program, error):
    """ Perform semantic analysis on an AST """
    verbose_report("Performing semantic analysis...")
    visitor = semantics.Semantics(error)
    program.accept(visitor)
    verbose_report("done.\n")

def pprint_ast(program):
    """ Pretty-print an AST in sire syntax """
    walker = printer.Printer()
    walker.walk_program(program)

def show_ast(program):
    """ Produce a formatted dump of an AST """
    visitor = dump.Dump()
    program.accept(visitor)

def translate_ast(program, buf):
    """ Transform an AST into XC """
    walker = translate.Translate(buf)
    walker.walk_program(program)
   
def verbose_report(msg):
    if verbose: sys.stdout.write(msg)

def main(args):
        
    # Setup parser and parse arguments
    argp = setup_argparse()
    a = argp.parse_args(args)
    global verbose
    verbose = a.verbose

    # Setup the error object
    err = error.Error()

    # Read the input file and parse
    input = read_input(a.infile) 
    program = parse(input, a.infile, err)
    verbose_report('Completed parsing.')

    # Perform semantic analysis
    semantic_analysis(program, err)
    if a.sem_only:
        return

    # Display (dump) the AST
    if a.show_ast:    
        show_ast(program)
        return

    # Display (pretty-print) the AST
    if a.pprint: 
        pprint_ast(program)
        return
   
    # Translate the AST
    buf = io.StringIO()
    translate_ast(program, buf)
    if a.translate_only: 
        write_output(buf, a.outfile)
        return

    # Compile
    pass
    os.remove(a.outfile)
    if a.compile_only: return

    # Assemble and link with the runtime
    pass

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
   
