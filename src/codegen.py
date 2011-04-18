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

from target.xs1.translate import TranslateXS1
from target.mpi.translate import TranslateMPI
from target.xs1.build import build_xs1
from target.mpi.build import build_mpi

DEFS_FILE_SUFFIX = 'definitions.h'

def translate(ast, sem, child, device, outfile, translate_only, v):
    """ Translate the AST to target system. 
    """
    vmsg(v, 'Translating AST...')

    buf = io.StringIO()
    ext = None

    # Create a tranlator AST walker
    if device.system == 'xs1':
        walker = TranslateXS1(sem, child, buf)
    elif device.system == 'mpi':
        walker = TranslateMPI(sem, child, buf)

    walker.walk_program(ast)
    
    if translate_only:
        outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
                outfile+'.'+device.source_file_ext())
        util.write_file(outfile, buf.getvalue())
        vmsg(v, 'Produced file: '+outfile+'\n')
        raise SystemExit()

    return buf

def build(sem, buf, device, outfile, compile_only, show_calls, v):
    """ Compile the translated AST for the target system.
    """
    vmsg(v, 'Creating executable...')

    # Create a Build object
    if device.system == 'xs1':
        build_xs1(sem, device, buf, outfile, compile_only, show_calls, v)
    elif device.system == 'mpi':
        build_mpi(sem, device, buf, outfile, compile_only, show_calls, v)

def generate(ast, sem, child, device, outfile, 
        translate_only, compile_only, show_calls, v):
    """ Generate code intermediate/machine/binary from AST.
    """

    # Load appropriate definitions for the system
    if device.system == 'xs1':
        defs.load(config.INCLUDE_PATH+'/xs1_'+DEFS_FILE_SUFFIX)
    elif device.system == 'mpi':
        defs.load(config.INCLUDE_PATH+'/mpi_'+DEFS_FILE_SUFFIX)
    
    # Translate the AST
    buf = translate(ast, sem, child, device, outfile, translate_only, v)
    
    # Compile, assemble and link with the runtime
    build(sem, buf, device, outfile, compile_only, show_calls, v)

