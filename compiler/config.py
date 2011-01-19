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
    
