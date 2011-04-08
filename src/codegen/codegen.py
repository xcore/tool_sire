# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast.ast as ast
import analysis.semantics as semantics
import analysis.children as children

from codegen.target.xs1.translate import TranslateXS1
from codegen.target.xs1.build import BuildXS1

from codegen.target.mpi.translate import TranslateMPI
from codegen.target.mpi.build import BuildMPI

def translate(ast, sem, child, target_system):
    """ Translate the AST to target system. 
    """
    verbose_msg('Translating AST for '+target_system+'\n')

    translate_buf = io.StringIO()

    # Create a tranlator AST walker
    if target_system == 'xs1':
        walker = TranslateXS1(sem, child, translate_buf)
    elif target_system == 'mpi':
        walker = TranslateMPI(sem, child, translate_buf)

    walker.walk_program(ast)
    
    if translate_only:
        util.write_file(outfile, translate_buf.getvalue())

    return translate_buf

def build(sem, buf, outfile, compile_only):
    """ Compile the translated AST for the target system.
    """
    verbose_msg('Compiling an executable for {} cores\n'
            .format(num_cores))

    # Create a Build object
    if target_system == 'xs1':
        builder = BuildXS1(num_cores, sem, verbose, show_calls)
    elif target_system == 'mpi':
        builder = BuildMPI(num_cores, sem, verbose, show_calls)

    builder.build(buf, outfile, compile_only)
    verbose_msg('Produced file: '+outfile+'\n')

def generate(ast, sem, child, target_system, num_cores, 
        translate_only, compile_only):
    """ Generate code intermediate/machine/binary from AST.
    """
    
    # Translate the AST
    buf = translate(ast, child)
    
    if translate_only:
        verbose_msg('Produced file: '+outfile+'\n')
        raise SystemExit()

    # Compile, assemble and link with the runtime
    build(sem, buf, outfile, compile_only)

