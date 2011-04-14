# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import io

import common.util as util
import common.definitions as defs
from common.util import vmsg

import ast.ast as ast
import analysis.semantics as semantics
import analysis.children as children

from codegen.target.xs1.translate import TranslateXS1
from codegen.target.xs1.build import build_xs1

from codegen.target.mpi.translate import TranslateMPI
from codegen.target.mpi.build import build_mpi

def translate(ast, sem, child, device, outfile, translate_only, v):
    """ Translate the AST to target system. 
    """
    vmsg(v, 'Translating AST for '+device.system+'\n')

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

def build(sem, buf, device, outfile, compile_only, v):
    """ Compile the translated AST for the target system.
    """
    vmsg(v, 'Compiling an executable for {} cores\n'.format(num_cores))

    # Create a Build object
    if device.system == 'xs1':
        build_xs1(sem, device, buf, outfile, compile_only, show_calls, v)
    elif device.system == 'mpi':
        build_mpi(sem, device, buf, outfile, compile_only, show_calls, v)

    verbose_msg('Produced file: '+outfile+'\n')

def generate(ast, sem, child, device, outfile, 
        translate_only, compile_only, v):
    """ Generate code intermediate/machine/binary from AST.
    """
    
    # Translate the AST
    buf = translate(ast, sem, child, device, outfile, translate_only, v)
    
    # Compile, assemble and link with the runtime
    build(sem, buf, device, outfile, compile_only, v)

