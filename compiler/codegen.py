# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import io

import util
import config
import definitions as defs
from util import vmsg
from util import vhdr
import ast
import semantics
import children

from target.definitions import *
from target.xs1.translate import TranslateXS1
from target.mpi.translate import TranslateMPI
from target.xs1.build import build_xs1
from target.mpi.build import build_mpi

DEFS_FILE = 'definitions.h'

def translate(ast, sig, child, device, outfile, translate_only, v):
  """ 
  Translate the AST to target system.
  """
  vmsg(v, 'Translating AST...')

  buf = io.StringIO()
  ext = None

  # Create a tranlator AST walker
  if device.system == SYSTEM_TYPE_XS1:
    walker = TranslateXS1(sig, child, buf)
  elif device.system == SYSTEM_TYPE_MPI:
    walker = TranslateMPI(sig, child, buf)

  walker.walk_program(ast)
  
  if translate_only:
    outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
        outfile+'.'+device.source_file_ext())
    util.write_file(outfile, buf.getvalue())
    vmsg(v, 'Produced file: '+outfile)
    raise SystemExit()

  return buf

def build(sig, buf, device, outfile, 
    compile_only, display_memory, show_calls, save_temps, v):
  """ 
  Compile the translated AST for the target system.
  """
  vmsg(v, 'Creating executable...')

  # Create a Build object
  if device.system == SYSTEM_TYPE_XS1:
    build_xs1(sig, device, buf, outfile, 
        compile_only, display_memory, show_calls, save_temps, v)
  elif device.system == SYSTEM_TYPE_MPI:
    build_mpi(device, buf, outfile, compile_only, show_calls, v)

def generate(ast, sig, child, device, outfile, 
    translate_only, compile_only, display_memory, 
    show_calls, save_temps, v):
  """ 
  Generate code intermediate/machine/binary from AST.
  """

  # Load appropriate definitions for the system
  if device.system == SYSTEM_TYPE_XS1:
    defs.load(config.XS1_SYSTEM_PATH+'/'+DEFS_FILE)
  elif device.system == SYSTEM_TYPE_MPI:
    defs.load(config.MPI_SYSTEM_PATH+'/'+DEFS_FILE)
  
  # Translate the AST
  buf = translate(ast, sig, child, device, outfile, translate_only, v)
  
  # Compile, assemble and link with the runtime
  build(sig, buf, device, outfile, compile_only, display_memory, 
      show_calls, save_temps, v)

