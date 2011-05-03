# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from error import Error
from target.xs1.device import get_xs1_device
from target.mpi.device import get_mpi_device

TARGET_SYSTEMS = ['xs1', 'mpi']
DEFAULT_TARGET_SYSTEM = TARGET_SYSTEMS[0]
DEFAULT_NUM_CORES = 1

def set_device(target_system, num_cores):
    """ Return a device object representing the target system with a specified
        number of cores.
    """
    # XS1
    if target_system == 'xs1':
        return get_xs1_device(num_cores)
    # MPI
    elif target_system == 'mpi':
        return get_mpi_device(num_cores)

    # Otherwise
    else:
        raise Error('invalid device')

