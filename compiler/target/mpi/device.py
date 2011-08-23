# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from target.definitions import *
from target.device import Device

class MPIDevice(Device):
    def __init__(self, name, num_nodes):
        super(MPIDevice, self).__init__(SYSTEM_TYPE_MPI, None, name, num_nodes)
    
    def source_file_ext(self):
        return MPI_SOURCE_FILE_EXT

    def assembly_file_ext(self):
        return MPI_ASSEMBLY_FILE_EXT

    def binary_file_ext(self):
        return MPI_BINARY_FILE_EXT

def get_mpi_device(num_cores):
    return MPIDevice(SYSTEM_TYPE_MPI, num_cores)

