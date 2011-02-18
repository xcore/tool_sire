#!/usr/bin/env python3.1

import os
import sys
import subprocess
import unittest

COMPILE          = 'sire'
SIMULATE         = 'xsim'
SIM_FLAGS        = []
INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'

class Test(object):
    def __init__(self, name, output, cores=[1], args=[]):
        self.name = name
        self.output = output
        self.cores = cores
        self.args = args

program_tests = [ 
    Test('hello',          'hello world\n'),
    Test('factorial-loop', '6\n120\n5040\n'),
    Test('factorial-rec',  '6\n120\n5040\n'),
    Test('fibonacci-loop', '8\n89\n987\n'),
    Test('fibonacci-rec',  '8\n89\n987\n'),
    Test('power',          '32\n729\n78125\n'),
    Test('ackermann',      '3\n11\n29\n'),
    Test('primetest',      '1010101000101000101000100\n'),
    Test('bubblesort',     '0123456789\n'),
    Test('quicksort',      '0123456789\n'),
    Test('mergesort-seq',  '0123456789\n'),
    Test('euclid-loop',    '8\n7\n1\n'),
    Test('euclid-rec',     '8\n7\n1\n'),
    Test('distribute',     '', [4, 16, 32, 64]),
]
    
thread_tests = [
    Test('thread_basic_2', ''),
    Test('thread_basic_4', ''),
    Test('thread_basic_8', ''),
]

on_tests = [
    Test('on_children', '', [4]),
    Test('on_basic', '', [4, 16, 32, 64]),
    Test('on_repeat_1', '', [4, 16]),
    Test('on_repeat_2', '', [4, 16]),
    Test('on_array', 'DEADBEEF\n', [4, 16, 32, 64]),
    Test('on_chain_1', '', [4, 16, 32, 64]),
    Test('on_chain_2', '', [4, 16, 32, 64]),
    Test('on_chain_3', '', [4, 16, 32, 64]),
    Test('on_chain_6', '', [4, 16, 32, 64]),
    Test('on_collision_1', '', [4, 16, 32, 64]),
    Test('on_collision_2', '', [4, 16, 32, 64]),
]

def init():
    """ Initialise configuration """
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

def run_test(self, name, path, output, num_cores, args=[]):
    """ Run a single test """
    r = call([COMPILE, path+'/'+name+'.sire'] 
            + ['-n', '{}'.format(num_cores)] + args)
    self.assertTrue(r[0])
    r = call([SIMULATE, 'a.xe'] + SIM_FLAGS)
    self.assertTrue(r[0])
    self.assertEqual(r[1], output)

def test_generator(name, path, output, num_cores):
    """ Generate the test harness """
    def test(self):
        run_test(self, name, path, output, num_cores)
    return test

def generate_program_tests():
    """ Dynamically generate all the program tests """
    for t in program_tests:
        for num_cores in t.cores:
            name = 'test_program_{}_{}'.format(t.name, num_cores)
            test = test_generator(t.name, TEST_PROGRAMS_PATH, t.output, num_cores)
            setattr(FeatureTests, name, test)

def generate_feature_tests():
    """ Dynamically generate all the feature tests """
    for t in thread_tests + on_tests:
        for num_cores in t.cores:
            name = 'test_feature_{}_{}'.format(t.name, num_cores)
            test = test_generator(t.name, TEST_FEATURES_PATH, t.output, num_cores)
            setattr(FeatureTests, name, test)

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

class FeatureTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    if init():
        sys.argv.append('-v')
        generate_program_tests()
        generate_feature_tests()
        unittest.main()
