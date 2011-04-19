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
EXAMPLES_DIR     = '/test/examples-old' 
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

def init():
    """ Initialise configuration
    """
    global INSTALL_PATH
    INSTALL_PATH = os.environ[INSTALL_PATH_ENV]
    if not INSTALL_PATH:
        raise Exception("Error: no '"+INSTALL_PATH_env+"' enviromnent variable", 
                out=sys.stderr)
    else:
        globals()['TEST_EXAMPLES_PATH'] = INSTALL_PATH+EXAMPLES_DIR
        globals()['TEST_FEATURES_PATH'] = INSTALL_PATH+FEATURES_DIR

if __name__ == '__main__':

    init()
    sys.argv.append('-v')

    # Generate MPI tests
    feature_tests = generate_mpi_feature_tests(TEST_FEATURES_PATH)
    example_tests = generate_mpi_example_tests(TEST_EXAMPLES_PATH)

    # Generate XS1 tests
    #feature_tests += generate_xs1_feature_tests(TEST_FEATURES_PATH)
    #example_tests += generate_xs1_example_tests(TEST_EXAMPLES_PATH)

    [setattr(FeatureTests, x.__name__, x) for x in feature_tests]
    [setattr(ExampleTests, x.__name__, x) for x in example_tests]
    
    # Run all the tests
    unittest.main()

