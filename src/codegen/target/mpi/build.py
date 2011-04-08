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

import common.definitions as defs
import common.util as util
import analysis.builtin as builtin
from codegen.build import Build

PROGRAM          = 'program'
PROGRAM_SRC      = PROGRAM+'.c'
PROGRAM_ASM      = PROGRAM+'.S'
PROGRAM_OBJ      = PROGRAM+'.o'

RUNTIME_FILES = ['guest.c', 'host.c', 'master.c', 'slave.c', 'system.c', 'util.c']

class BuildMPI(Build):

    def compile_asm(self, program_buf, outfile, device):
        """ Compile the translated program into assembly.
        """

        # ...

        # Write the program back out and assemble
        if s: s = util.write_file(PROGRAM_ASM, ''.join(lines))

        # Rename the output file
        if s: os.rename(PROGRAM_ASM, outfile)
        
        return s

    def compile_binary(self, program_buf, outfile, device):
        """ Run the full build
        """
        
        # ...

        self.cleanup(outfile)
        return s

    def cleanup(self, output_xe):
        """ Renanme the output file and delete any temporary files
        """
        self.verbose_msg('Cleaning up')
        
        # Remove specific files
        #util.remove_file(DEVICE_HDR)
        
        # Remove unused master images
        #for x in glob.glob('image_n*c*elf'):
        #    util.remove_file(x)

        # Remove runtime objects
        #for x in glob.glob('*.o'):
        #    util.remove_file(x)


