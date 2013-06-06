# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import os

INSTALL_PATH_ENV = 'SIRE_HOME'

def init():
  """
  Initialise configuration variables.
  """
  global INSTALL_PATH
  INSTALL_PATH = os.environ[INSTALL_PATH_ENV]

  if INSTALL_PATH:
    init_paths()
  else:
    raise Exception("no '"+INSTALL_PATH_env+"' enviromnent variable")

def init_paths():
  """
  Initialise various paths.
  """
  globals()['SYSTEM_PATH']      = INSTALL_PATH+'/system'
  
  globals()['XS1_DEVICE_PATH']  = INSTALL_PATH+'/device/xs1'
  globals()['XS1_SYSTEM_PATH']  = INSTALL_PATH+'/system/xs1'
  globals()['XS1_RUNTIME_PATH'] = INSTALL_PATH+'/runtime/xs1'
  
  globals()['MPI_SYSTEM_PATH']  = INSTALL_PATH+'/system/mpi'
  globals()['MPI_RUNTIME_PATH'] = INSTALL_PATH+'/runtime/mpi'
  
