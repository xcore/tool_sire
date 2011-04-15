# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import os
import io
import re
import glob
import subprocess
from math import floor

import definitions as defs
import config
import util
from util import vmsg
from error import Error
import builtin

DEVICE_HDR       = 'device.h'
PROGRAM          = 'program.c'
BINARY           = 'a.out'

MPICC            = 'mpicc'
COMPILE_FLAGS    = ['-S', '-O2']
ASSEMBLE_FLAGS   = ['-c', '-O2']
LINK_FLAGS       = []

RUNTIME_FILES = ['main.c']

def build_mpi(sem, device, buf, outfile, 
        compile_only, show_calls=False, v=False):
    """ Run the build process to create either the assembly output or the
        complete binary.
    """
    # Add the include paths once they have been set
    include_dirs = ['-I', config.MPI_RUNTIME_PATH]
    include_dirs += ['-I', config.INCLUDE_PATH]
    include_dirs += ['-I', '.']
    
    global COMPILE_FLAGS
    global ASSEMBLE_FLAGS
    COMPILE_FLAGS += include_dirs
    ASSEMBLE_FLAGS += include_dirs

    try:
        
        # Create headers
        create_headers(device, v)

        if compile_only:
            raise SystemExit() 

        # Compile the program and runtime
        assemble_str(PROGRAM, buf.getvalue(), show_calls, v)
        buf.close()
        assemble_runtime(show_calls, v)
        link(show_calls, v)

        # Rename the output file
        outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
                outfile+'.'+device.binary_file_ext())
        os.rename(BINARY, outfile)

        vmsg(v, 'Produced file: '+outfile)

    finally:
        #cleanup(v)
        pass

def create_headers(device, v):
    vmsg(v, 'Creating device header '+DEVICE_HDR)
    s =  '#define NUM_CORES {}\n'.format(device.num_cores())
    util.write_file(DEVICE_HDR, s)

def assemble_str(name, string, show_calls, v, cleanup=True):
    """ Assemble a buffer containing a c program
    """
    srcfile = name + '.c'
    outfile = name + '.o'
    vmsg(v, 'Assembling '+srcfile+' -> '+outfile)
    util.write_file(srcfile, string)
    util.call([MPICC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS, show_calls)
    if cleanup: 
        os.remove(srcfile)

def assemble_runtime(show_calls, v):
    vmsg(v, 'Compiling runtime:')
    for x in RUNTIME_FILES:
        objfile = x+'.o'
        vmsg(v, '  '+x+' -> '+objfile)
        util.call([MPICC, config.MPI_RUNTIME_PATH+'/'+x, 
            '-o', objfile] + ASSEMBLE_FLAGS, show_calls)

def link(show_calls, v):
    """ The jump table must be located at _cp and the common elements of the
        constant and data pools must be in the same positions relative to _cp
        and _dp in the master and slave images.
    """
    vmsg(v, 'Linking executable -> '+BINARY)
    util.call([MPICC, 
        'main.c.o', 'program.c.o',
        '-o', BINARY] + LINK_FLAGS, show_calls)

def cleanup(v):
    """ Renanme the output file and delete any temporary files
    """
    vmsg(v, 'Cleaning up')
    
    # Remove specific files
    util.remove_file(DEVICE_HDR)
    
    # Remove runtime objects
    for x in glob.glob('*.o'):
        util.remove_file(x)
