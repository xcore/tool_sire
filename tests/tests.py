#!/usr/bin/env python3.1

import os
import sys
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
        """ Execute a shell command, return (success, output)
        """
        try:
            # Returning non-zero will riase CalledProcessError
            s = subprocess.check_output(args, stderr=subprocess.STDOUT)
            return (True, s.decode('utf-8'))
        except subprocess.CalledProcessError as err:
            s = err.output.decode('utf-8').replace("\\n", "\n")
            print('Error executing command:\n{}\nOuput:\n{}'.format(err.cmd, s))
            return (False, None)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def harness(self, filename, output):
        r = self.call([COMPILE, TEST_PROGRAMS_PATH+'/'+filename])
        self.assertTrue(r[0])
        r = self.call([SIMULATE, 'a.xe'])
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)

    def test_program_hello(self):
        self.harness('hello.sire', 'hello world\n')

    def test_program_factorial_loop(self):
        self.harness('factorial-loop.sire', '6\n120\n5040\n')

    def test_program_factorial_rec(self):
        self.harness('factorial-rec.sire', '6\n120\n5040\n')

    def test_program_fibonacci_loop(self):
        self.harness('fibonacci-loop.sire', '8\n89\n987\n')

    def test_program_fibonacci_rec(self):
        self.harness('fibonacci-rec.sire', '8\n89\n987\n')

    # ackermann
    # power
    # primetest
    # bubblesort
    # mergesort-seq
    # quicksort

if __name__ == '__main__':
    if init():
        sys.argv.append('-v')
        unittest.main()
