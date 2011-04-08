# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import common.config as config

class Build(object):
    """ A class to compile, assemble and link the program source with the
        runtime into an executable binary. This class is extended by particular
        targets which implement compile_asm() and compile_binary().
    """
    def __init__(self, num_cores, semantics, verbose=False, showcalls=False):
        self.num_cores = num_cores
        self.sem = semantics
        self.verbose = verbose
        self.showcalls = showcalls

        # Add the include paths once they have been set
        global COMPILE_FLAGS
        global ASSEMBLE_FLAGS
        include_dirs = ['-I', config.XS1_RUNTIME_PATH]
        include_dirs += ['-I', config.INCLUDE_PATH]
        include_dirs += ['-I', '.']
        COMPILE_FLAGS += include_dirs
        ASSEMBLE_FLAGS += include_dirs

    def build(self, program_buf, outfile, compile_only):
        """ Run the build process to create either the assembly output or the
            complete binary.
        """
        if compile_only:
            compile_asm(program_buf, outfile, None)
        else:
            compile_binary(program_buf, outfile, None)
    
    def verbose_msg(self, msg, end='\n'):
        """ Output a message that is displayed in verbose mode.
        """
        if self.verbose: 
            sys.stdout.write(msg+end)
            sys.stdout.flush()
    
