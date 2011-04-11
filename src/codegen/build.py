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
    def __init__(self, semantics, device, verbose=False, showcalls=False):
        self.device = device
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
            compile_asm(program_buf, self.device, outfile)
        else:
            compile_binary(program_buf, device, outfile)
    
