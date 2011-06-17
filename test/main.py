#!/usr/bin/env python3

# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import os
import sys
import unittest

from tests_mpi import generate_mpi_example_tests
from tests_mpi import generate_mpi_feature_tests
from tests_xs1 import generate_xs1_example_tests
from tests_xs1 import generate_xs1_feature_tests

INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'
EXAMPLES_DIR     = '/test/examples' 
FEATURES_DIR     = '/test/features' 

class ExampleTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

class FeatureTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

def fail(argv):
    sys.exit('Usage: '+argv[0]+' {xs1,mpi}')

if __name__ == '__main__':

    # Check we have a test target
    if len(sys.argv) < 2:
        fail(sys.argv)

    # Initialise global paths
    global INSTALL_PATH
    INSTALL_PATH = os.environ[INSTALL_PATH_ENV]
    if not INSTALL_PATH:
        raise Exception("Error: no '"+INSTALL_PATH_env+"' enviromnent variable", 
                out=sys.stderr)
    else:
        globals()['TEST_EXAMPLES_PATH'] = INSTALL_PATH+EXAMPLES_DIR
        globals()['TEST_FEATURES_PATH'] = INSTALL_PATH+FEATURES_DIR
    
    feature_tests = []
    example_tests = []

    # Generate tests for the specified target
    if sys.argv[1] == 'mpi':
        feature_tests += generate_mpi_feature_tests(TEST_FEATURES_PATH)
        example_tests += generate_mpi_example_tests(TEST_EXAMPLES_PATH)

    elif sys.argv[1] == 'xs1':
        feature_tests += generate_xs1_feature_tests(TEST_FEATURES_PATH)
        #example_tests += generate_xs1_example_tests(TEST_EXAMPLES_PATH)
    
    else:
        fail(sys.argv)

    [setattr(FeatureTests, x.__name__, x) for x in feature_tests]
    [setattr(ExampleTests, x.__name__, x) for x in example_tests]
    
    # Run all the tests
    sys.argv.pop()
    sys.argv.append('-v')
    unittest.main()

