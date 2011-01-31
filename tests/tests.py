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
        globals()['TEST_FEATURES_PATH'] = INSTALL_PATH+'/tests/features'
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

    def program(self, filename, output, args=[]):
        r = self.call([COMPILE, TEST_PROGRAMS_PATH+'/'+filename] + args)
        self.assertTrue(r[0])
        r = self.call([SIMULATE, 'a.xe'])
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)

    def feature(self, filename, output, args=[]):
        r = self.call([COMPILE, TEST_FEATURES_PATH+'/'+filename] + args)
        self.assertTrue(r[0])
        r = self.call([SIMULATE, 'a.xe'])
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)

    # Programs =================================================

    def test_program_hello(self):
        self.program('hello.sire', 'hello world\n')

    def test_program_factorial_loop(self):
        self.program('factorial-loop.sire', '6\n120\n5040\n')

    def test_program_factorial_rec(self):
        self.program('factorial-rec.sire', '6\n120\n5040\n')

    def test_program_fibonacci_loop(self):
        self.program('fibonacci-loop.sire', '8\n89\n987\n')

    def test_program_fibonacci_rec(self):
        self.program('fibonacci-rec.sire', '8\n89\n987\n')

    def test_program_power(self):
        self.program('power.sire', '32\n729\n78125\n')

    def test_program_ackermann(self):
        self.program('ackermann.sire', '3\n11\n29\n')

    def test_program_primetest(self):
        self.program('primetest.sire', '1010101000101000101000100\n')

    def test_program_bubblesort(self):
        self.program('bubblesort.sire', '0123456789\n')

    def test_program_quicksort(self):
        self.program('quicksort.sire', '0123456789\n')

    def test_program_mergesort_seq(self):
        self.program('mergesort-seq.sire', '0123456789\n')

    def test_program_euclid_loop(self):
        self.program('euclid-loop.sire', '8\n7\n1\n')

    def test_program_euclid_rec(self):
        self.program('euclid-rec.sire', '8\n7\n1\n')

    # Features =================================================

    def test_feature_on_basic(self):
        self.feature('on_basic', '', ['-n', '4'])

    def test_feature_on_array(self):
        self.feature('on_array', 'DEADBEEF', ['-n', '4'])

if __name__ == '__main__':
    if init():
        sys.argv.append('-v')
        unittest.main()
