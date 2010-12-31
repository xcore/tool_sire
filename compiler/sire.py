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

def setup_argparse():
    """ Configure an argument parser object """
    p = argparse.ArgumentParser(description='sire compiler')
    p.add_argument('infile', metavar='input-file')
    p.add_argument('outfile', metavar='output-file', nargs='?')
    p.add_argument('-s', '--sem', action='store_true', dest='sem_only', 
            help='perform semantic analysis and quit')
    p.add_argument('-a', '--ast', action='store_true', dest='show_ast',
            help='display the AST and quit')
    p.add_argument('-p', '--pprint', action='store_true', dest='pprint',
            help='pretty-print the AST and quit')
    return p

def read_input(filename):
    """ Read a file and return its contents as a string """
    try:
        file = open(filename, 'r')
        contents = file.read()
        file.close()
    except(IOError, (errno, stderror)):
        print('I/O error({}): {}'.format(errno, stderror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])
    return contents

def write_output(buf, outfile):
    """ Write the output to a file """
    try:
        file = open(outfile, 'w')
        translate_ast(program, file)
        file.close()
    except IOError as err:
        print('I/O error({}): {}'.format(err.errno, err.stderror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])

def parse(input, filename, error, logging=False):
    """ Parse an input string to produce an AST """
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
    return program

def semantic_analysis(program, error):
    """ Perform semantic analysis on an AST """
    visitor = semantics.Semantics(error)
    program.accept(visitor)

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
    
def main(args):

    # Setup parser and parse arguments
    argp = setup_argparse()
    a = argp.parse_args(args)

    # Setup the error object
    err = error.Error()

    # Read the input file and parse
    input = read_input(a.infile) 
    program = parse(input, a.infile, err)

    # Perform semantic analysis
    semantic_analysis(program, err)
    if a.sem_only: return

    if a.show_ast:    
        show_ast(program)
        return

    if a.pprint: 
        pprint_ast(program)
        return
   
    # Translate the ast and write the output to a file
    buf = io.StringIO()
    translate_ast(program, buf)
    write_output(buf, 'out.xc')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
       
