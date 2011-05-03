# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from target.device import Device

MPI_SOURCE_FILE_EXT = 'c'
MPI_ASSEMBLY_FILE_EXT = 'S'
MPI_BINARY_FILE_EXT = 'out'

class MPIDevice(Device):
    def __init__(self, name, num_nodes):
        super(MPIDevice, self).__init__('mpi', name, num_nodes)
    
    def source_file_ext(self):
        return MPI_SOURCE_FILE_EXT

    def assembly_file_ext(self):
        return MPI_ASSEMBLY_FILE_EXT

    def binary_file_ext(self):
        return MPI_BINARY_FILE_EXT

def get_mpi_device(num_cores):
    return MPIDevice('MPI', num_cores)

