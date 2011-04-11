# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from codegen.target.device import Device

SOURCE_FILE_EXT = 'c'
ASSEMBLY_FILE_EXT = 'S'
BINARY_FILE_EXT = None

class MPIDevice(Device):
    def __init__(self, name, num_nodes):
        super(XS1Device, self).__init__('mpi', name, num_nodes)
    
    def get_source_file_ext(self):
        return SOURCE_FILE_EXT

    def get_assembly_file_ext(self):
        return ASSEMBLY_FILE_EXT

    def get_binary_file_ext(self):
        return BINARY_FILE_EXT

def get_xs1_device(num_cores):
    return MPIDevice('MPI', num_cores)

