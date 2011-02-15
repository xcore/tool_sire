#!/usr/bin/env python3.1

import os
import sys
import subprocess
import unittest

COMPILE          = 'sire'
SIMULATE         = 'xsim'
SIM_FLAGS        = ['--iss']
PROGRAM_DIR      = 'programs'
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

def call(args):
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


class ProgramTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def program(self, filename, output, args=[]):
        r = call([COMPILE, TEST_PROGRAMS_PATH+'/'+filename+'.sire'] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, 'a.xe'] + SIM_FLAGS)
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)

    # Programs =================================================
    
    def test_program_hello(self):
        self.program('hello', 'hello world\n')

    def test_program_factorial_loop(self):
        self.program('factorial-loop', '6\n120\n5040\n')

    def test_program_factorial_rec(self):
        self.program('factorial-rec', '6\n120\n5040\n')

    def test_program_fibonacci_loop(self):
        self.program('fibonacci-loop', '8\n89\n987\n')

    def test_program_fibonacci_rec(self):
        self.program('fibonacci-rec', '8\n89\n987\n')

    def test_program_power(self):
        self.program('power', '32\n729\n78125\n')

    def test_program_ackermann(self):
        self.program('ackermann', '3\n11\n29\n')

    def test_program_primetest(self):
        self.program('primetest', '1010101000101000101000100\n')

    def test_program_bubblesort(self):
        self.program('bubblesort', '0123456789\n')

    def test_program_quicksort(self):
        self.program('quicksort', '0123456789\n')

    def test_program_mergesort_seq(self):
        self.program('mergesort-seq', '0123456789\n')

    def test_program_euclid_loop(self):
        self.program('euclid-loop', '8\n7\n1\n')

    def test_program_euclid_rec(self):
        self.program('euclid-rec', '8\n7\n1\n')

    # distribute
    def test_program_distribute_4(self):
        self.program('distribute', '', ['-n', '4'])

    def test_program_distribute_16(self):
        self.program('distribute', '', ['-n', '16'])

    def test_program_distribute_64(self):
        self.program('distribute', '', ['-n', '64'])


class FeatureTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def feature(self, filename, output, args=[]):
        r = call([COMPILE, TEST_FEATURES_PATH+'/'+filename+'.sire'] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, 'a.xe'] + SIM_FLAGS)
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)

    # Features =================================================
   
    # on_basic
    def test_feature_on_basic_4(self):
        self.feature('on_basic', '', ['-n', '4'])

    def test_feature_on_basic_16(self):
        self.feature('on_basic', '', ['-n', '16'])

    def test_feature_on_basic_64(self):
        self.feature('on_basic', '', ['-n', '64'])

    # on_array
    def test_feature_on_array_4(self):
        self.feature('on_array', 'DEADBEEF\n', ['-n', '4'])

    def test_feature_on_array_16(self):
        self.feature('on_array', 'DEADBEEF\n', ['-n', '16'])

    def test_feature_on_array_64(self):
        self.feature('on_array', 'DEADBEEF\n', ['-n', '64'])

    # on_chain
    def test_feature_on_chain_4(self):
        self.feature('on_chain', '', ['-n', '4'])

    def test_feature_on_chain_16(self):
        self.feature('on_chain', '', ['-n', '16'])

    def test_feature_on_chain_64(self):
        self.feature('on_chain', '', ['-n', '64'])

    # on_children
    def test_feature_on_children_4(self):
        self.feature('on_children', '', ['-n', '4'])

    # thread_basic
    def test_feature_thread_basic_2(self):
        self.feature('thread_basic_2', '')

    def test_feature_thread_basic_4(self):
        self.feature('thread_basic_4', '')

    def test_feature_thread_basic_8(self):
        self.feature('thread_basic_8', '')

    # on_chain_threaded_2
    def test_feature_on_chain_threaded_2_4(self):
        self.feature('on_chain_threaded_2', '', ['-n', '4'])

    def test_feature_on_chain_threaded_2_16(self):
        self.feature('on_chain_threaded_2', '', ['-n', '16'])

    #def test_feature_on_chain_threaded_2_64(self):
    #    self.feature('on_chain_threaded_2', '', ['-n', '64'])

    # on_chain_threaded_3
    def test_feature_on_chain_threaded_3_4(self):
        self.feature('on_chain_threaded_3', '', ['-n', '4'])

    def test_feature_on_chain_threaded_3_16(self):
        self.feature('on_chain_threaded_3', '', ['-n', '16'])

    #def test_feature_on_chain_threaded_3_64(self):
    #    self.feature('on_chain_threaded_3', '', ['-n', '64'])

    # on_chain_threaded_8
    def test_feature_on_chain_threaded_8_4(self):
        self.feature('on_chain_threaded_8', '', ['-n', '4'])

    def test_feature_on_chain_threaded_8_16(self):
        self.feature('on_chain_threaded_8', '', ['-n', '16'])

    #def test_feature_on_chain_threaded_8_64(self):
    #    self.feature('on_chain_threaded_8', '', ['-n', '64'])

if __name__ == '__main__':
    if init():
        sys.argv.append('-v')
        unittest.main()
