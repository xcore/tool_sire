# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from codegen.target.xs1.device import AVAILABLE_XS1_DEVICES
from codegen.target.mpi.device import MPIDevice

TARGET_SYSTEMS = ['xs1', 'mpi']
DEFAULT_NUM_CORES = 1

class Device(object):
    """ A generic class to represent a target device.
    """
    def __init__(self, system, name, num_nodes):
        self.name = name
        self.system = system
        self.num_nodes = num_nodes

    def num_cores(self):
        return self.num_nodes


def set_device(target_system, num_cores):
    """ Check for a valid available device and return it.
    """
    # XS1
    if target_system == 'xs1':
        d = [x for x in AVAILABLE_XS1_DEVICES if num_cores==x.num_cores()]
        if d:
            return d[0]
        else:
            raise Error('invalid XS1 target ({} cores)'.format(num_cores))

    # MPI
    elif target_system == 'mpi':
        return MPIDevice(num_cores)

    # Otherwise
    else:
        raise Error('invalid device')

