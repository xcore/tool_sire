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
import util
import builtin

PROGRAM          = 'program'
PROGRAM_SRC      = PROGRAM+'.c'
PROGRAM_ASM      = PROGRAM+'.S'
PROGRAM_OBJ      = PROGRAM+'.o'

RUNTIME_FILES = ['guest.c', 'host.c', 'master.c', 'slave.c', 'system.c', 'util.c']

def build_mpi(self, semantics, device, program_buf, outfile, compile_only, 
        verbose=False, showcalls=False):
    """ Run the build process to create either the assembly output or the
        complete binary.
    """
    # Add the include paths once they have been set
    include_dirs = ['-I', config.XS1_RUNTIME_PATH]
    include_dirs += ['-I', config.INCLUDE_PATH]
    include_dirs += ['-I', '.']
    
    global COMPILE_FLAGS
    global ASSEMBLE_FLAGS
    COMPILE_FLAGS += include_dirs
    ASSEMBLE_FLAGS += include_dirs

    try:
        
        # ...
        
        if compile_only:
            
            # Write the program back out and assemble
            util.write_file(PROGRAM_ASM, ''.join(lines))

            # Rename the output file
            outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
                    outfile+'.'+device.assembly_file_ext())
            os.rename(PROGRAM_ASM, outfile)

            raise SystemExit() 

        # ...

        # Write the program back out and assemble
        if s: s = util.write_file(PROGRAM_ASM, ''.join(lines))

        # Rename the output file
        if s: os.rename(PROGRAM_ASM, outfile)
        
        # Rename the output file
        outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
                outfile+'.'+device.binary_file_ext())
        os.rename(SLAVE_XE, outfile)

        vmsg(v, 'Produced file: '+outfile)

    except Error as e:
        cleanup()
        raise Error(e.args)
    
    except SystemExit:
        raise SystemExit()
  
    except:
        raise
        
    finally:
        cleanup(v)

def cleanup(self, output_xe):
    """ Renanme the output file and delete any temporary files
    """
    self.verbose_msg('Cleaning up')
    
    # Remove specific files
    #util.remove_file(DEVICE_HDR)
    
    # Remove runtime objects
    for x in glob.glob('*.o'):
        util.remove_file(x)

