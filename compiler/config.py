# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import os

INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'

def init(error):
    """ Initialise configuration variables
    """
    global INSTALL_PATH
    INSTALL_PATH = os.environ[INSTALL_PATH_ENV]
    if INSTALL_PATH:
        init_paths()
        return True
    else:
        error.fatal("no '"+INSTALL_PATH_env+"' enviromnent variable")
        return False

def init_paths():
    
    globals()['INCLUDE_PATH'] = INSTALL_PATH+'/include'
    globals()['DEVICE_PATH']  = INSTALL_PATH+'/devices'
    globals()['RUNTIME_PATH'] = INSTALL_PATH+'/runtime'
    
