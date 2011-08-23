# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

SYSTEM_TYPE_XS1       = 'XS1'
SYSTEM_TYPE_MPI       = 'MPI'

TARGET_SYSTEMS        = [SYSTEM_TYPE_XS1, SYSTEM_TYPE_MPI]
DEFAULT_TARGET_SYSTEM = SYSTEM_TYPE_XS1
DEFAULT_NUM_CORES     = 1

# XS1 definitions

XS1_SOURCE_FILE_EXT   = 'xc'
XS1_ASSEMBLY_FILE_EXT = 'S'
XS1_BINARY_FILE_EXT   = 'xe'

XS1_DEVICE_TYPE_G     = 'G'
XS1_DEVICE_TYPE_L     = 'L'

# MPI definitions

MPI_SOURCE_FILE_EXT   = 'c'
MPI_ASSEMBLY_FILE_EXT = 'S'
MPI_BINARY_FILE_EXT   = 'out'

