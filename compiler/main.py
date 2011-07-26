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

from error import Error, QuietError
from errorlog import ErrorLog
from util import vmsg, vhdr
import util
import config
import definitions as defs
from parser import Parser
from dump import Dump
from printer import Printer
from symbol import SymbolTable
from signature import SignatureTable
from semantics import Semantics
from buildcfg import BuildCFG
from liveness import Liveness
from insertons import InsertOns
from labelprocs import LabelProcs
from labelchans import LabelChans
from insertids import InsertIds
from insertconns import InsertConns
from renamechans import RenameChans
from transformpar import TransformPar
from transformrep import TransformRep
from flattencalls import FlattenCalls
from children import Children

from codegen import generate
from target.config import set_device
from target.config import TARGET_SYSTEMS
from target.config import DEFAULT_NUM_CORES
from target.config import DEFAULT_TARGET_SYSTEM

# Globals
v = False

def setup_argparse():
  """ 
  Configure an argument parser object.
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
  
  p.add_argument('-p', '--p-ast', action='store_true', dest='print_ast',
      help='display the AST and quit')
    
  p.add_argument('-P', '--ppr-ast', action='store_true', dest='pprint_raw_ast',
      help='pretty-print the raw AST and quit')
  
  p.add_argument('-Q', '--ppt-ast', action='store_true', dest='pprint_trans_ast',
      help='pretty-print the transformed AST and quit')
  
  p.add_argument('-T', '--translate', action='store_true',
      dest='translate_only',
      help='translate but do not compile')
  
  p.add_argument('-C', '--compile', action='store_true',
      dest='compile_only',
      help='compile but do not assemble and link')
  
  return p

def setup_globals(a):
  """ 
  Setup global variables representing compilation parameters.
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
  global pprint_raw_ast
  global pprint_trans_ast
  global parse_only
  global sem_only
  global translate_only
  global compile_only
  parse_only = a.parse_only
  sem_only = a.sem_only
  compile_only = a.compile_only
  print_ast = a.print_ast
  pprint_raw_ast = a.pprint_raw_ast
  pprint_trans_ast = a.pprint_trans_ast
  translate_only = a.translate_only
  compile_only = a.compile_only

  # Input/output targets
  global infile
  global outfile
  infile = a.infile
  outfile = a.outfile[0] if a.outfile else defs.DEFAULT_OUT_FILE

def produce_ast(input_file, errorlog, log=True):
  """ 
  Parse an input string to produce an AST.
  """
  vmsg(v, "Parsing file '{}'".format(infile if infile else 'stdin'))
   
  # Setup logging if we need to
  if log:
    logging.basicConfig(
      level = logging.DEBUG,
      filename = defs.PARSE_LOG_FILE,
      filemode = "w",
      format = "%(filename)10s:%(lineno)4d:%(message)s")
    logger = logging.getLogger()
  else:
    logger = 0
   
  # Create the parser and produce the AST
  parser = Parser(errorlog, lex_optimise=True, 
      yacc_debug=False, yacc_optimise=False)
  ast = parser.parse(input_file, infile, debug=logger)
  
  if errorlog.any():
    raise QuietError()
  
  # Perform parsing only
  if parse_only: 
    raise SystemExit()
  
  # Display (dump) the AST
  if print_ast:
    ast.accept(Dump())
    raise SystemExit()

  # Display (pretty-print) the AST
  if pprint_raw_ast: 
    Printer().walk_program(ast)
    raise SystemExit()

  return ast

def semantic_analysis(sym, sig, ast, device, errorlog):
  """ 
  Perform semantic analysis on an AST.
  """
  vmsg(v, "Performing semantic analysis")
  sem = Semantics(sym, sig, device, errorlog)
  sem.walk_program(ast)
  
  # Check for any errors
  if errorlog.any():
    raise QuietError()
   
  # Quit if we're only performing semantic analysis
  if sem_only: 
    raise SystemExit()

  return sem

def transform_ast(sem, sym, sig, ast, errorlog, device):
  """
  Perform transformations on the AST.
  """

  # 1. Move processes
  vmsg(v, "Inserting on statements")
  InsertOns().walk_program(ast)

  # 2. Label processes
  vmsg(v, "Labelling processes")
  LabelProcs(sym, device).walk_program(ast)

  # 3. Label channels
  vmsg(v, "Labelling channels")
  LabelChans(errorlog).walk_program(ast)
  if errorlog.any(): raise Error('in channel labelling')

  # 4. Insert procid()s
  vmsg(v, "Inserting process ids")
  InsertIds().walk_program(ast)

  # 5. Insert channel ends
  vmsg(v, "Inserting connections")
  InsertConns(sym).walk_program(ast)

  # 6. Rename channel uses
  vmsg(v, "Renaming channel uses")
  RenameChans().walk_program(ast)
  
  # 7. Build the control-flow graph and initialise sets for liveness analysis
  vmsg(v, "Building the control flow graph")
  BuildCFG().run(ast)

  # 8. Perform liveness analysis
  vmsg(v, "Performing liveness analysis")
  Liveness().run(ast)

  # 9. Transform parallel composition
  vmsg(v, "Transforming parallel composition")
  TransformPar(sem, sig).walk_program(ast)
  
  # 10. Transform parallel replication
  vmsg(v, "Transforming parallel replication")
  TransformRep(sym, sem, sig, device).walk_program(ast)
  
  # 11. Flatten nested calls
  vmsg(v, "Flattening nested calls")
  FlattenCalls(sig).walk_program(ast)
   
  # 12. Perform child analysis
  vmsg(v, "Performing child analysis")
  child = child_analysis(sig, ast)

  # Display (pretty-print) the transformed AST
  if pprint_trans_ast: 
    Printer().walk_program(ast)
    raise SystemExit()

  return child

def child_analysis(sig, ast):
  """ 
  Determine children.
  """
  child = Children(sig)
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
    sym = SymbolTable(errorlog)
    sig = SignatureTable(errorlog)
    sem = semantic_analysis(sym, sig, ast, device, errorlog)
    
    # Perform AST transformations
    child = transform_ast(sem, sym, sig, ast, errorlog, device)

    # Generate code
    vhdr(v, 'Generating code for {}'.format(device))
    generate(ast, sig, child, device, outfile, 
        translate_only, compile_only, show_calls, v)

  # Handle (expected) system exits
  except SystemExit:
    return 0

  # Handle any specific compilation errors quietly
  except QuietError as e:
    return 1
  
  # Handle any specific compilation errors
  except Error as e:
    sys.stderr.write('Error: {}\n'.format(e))
    return 1
  
  # Parser attribute error
  #except AttributeError:
  #  sys.stderr.write('Attribute error')
  #  return 1

  # Handle a keyboard interrupt (ctrl+c)
  except KeyboardInterrupt:
    sys.stderr.write('Interrupted')
    return 1
  
  # Anything else we weren't expecting
  except:
    sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
    raise
    return 1
  
  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
   
