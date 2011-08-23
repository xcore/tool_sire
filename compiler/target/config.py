# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from error import Error
from target.definitions import *
from target.xs1.device import get_xs1_device
from target.mpi.device import get_mpi_device

def set_device(target_system, num_cores):
  """ 
  Return a device object representing the target system with a specified
  number of cores.
  """
  # XS1
  if target_system == SYSTEM_TYPE_XS1:
    return get_xs1_device(num_cores)
  # MPI
  elif target_system == SYSTEM_TYPE_MPI:
    return get_mpi_device(num_cores)

  # Otherwise
  else:
    raise Error('invalid device')

