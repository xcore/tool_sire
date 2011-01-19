#!/usr/bin/env python3.1

import os
import subprocess
import unittest

COMPILE = 'sire'
SIMULATE = 'xsim'
PROGRAM_DIR = 'programs'
INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'

def init():
    """ Initialise configuration
    """
    global INSTALL_PATH
    INSTALL_PATH = os.environ[INSTALL_PATH_ENV]
    if not INSTALL_PATH:
        print("Error: no '"+INSTALL_PATH_env+"' enviromnent variable", 
                out=sys.stderr)
        return False
    else:
        globals()['TEST_PROGRAMS_PATH'] = INSTALL_PATH+'/tests/programs'
        return True

class Test(unittest.TestCase):

    def call(self, args):
        """ Execute a shell command
        """
        try:
            s = subprocess.check_output(args, stderr=subprocess.STDOUT)
            return s.decode('utf-8')
        except subprocess.CalledProcessError as err:
            s = err.output.decode('utf-8').replace("\\n", "\n")
            print('Error executing command:\n{}\nOuput:\n{}'.format(err.cmd, s))
            return None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        s = self.call([COMPILE, TEST_PROGRAMS_PATH+'/hello.sire'])
        self.assertTrue(s == None)
        s = self.call([SIMULATE, 'a.xe'])
        self.assertEqual(s, 'hello world\n')

if __name__ == '__main__':
    if init():
        unittest.main()
