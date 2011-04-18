# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import unittest

from util import call
from tests import Test

COMPILE          = 'sire'
SIMULATE         = 'xsim'
SIM_FLAGS        = []
INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'
EXAMPLES_DIR     = '/test/examples-old' 
FEATURES_DIR     = '/test/features' 

class XS1Test(Test):
    def __init__(self, test, cores=[1]):
        super(XS1Test, self).__init__(test.name, test.output, test.args)
        self.cores = cores


xs1_example_tests = [ 
  XS1Test(example_tests['hello'         ], [1, 4, 16, 32, 64]),
  XS1Test(example_tests['factorial-loop']),
  XS1Test(example_tests['factorial-rec' ]),
  XS1Test(example_tests['fibonacci-loop']),
  XS1Test(example_tests['fibonacci-rec' ]),
  XS1Test(example_tests['power'         ]),
  XS1Test(example_tests['ackermann'     ]),
  XS1Test(example_tests['primetest'     ]),
  XS1Test(example_tests['bubblesort'    ]),
  XS1Test(example_tests['quicksort'     ]),
  XS1Test(example_tests['mergesort-seq' ]),
  XS1Test(example_tests['mergesort-par' ], [4, 16]),
  XS1Test(example_tests['euclid-loop'   ]),
  XS1Test(example_tests['euclid-rec'    ]),
  XS1Test(example_tests['distribute'    ], [4, 16, 32, 64]),
]
    
xs1_thread_tests = [
  XS1Test(thread_tests['thread_basic_2' ]),
  XS1Test(thread_tests['thread_basic_4' ]),
  XS1Test(thread_tests['thread_basic_8' ]),
  XS1Test(thread_tests['thread_repeat_2']),
  XS1Test(thread_tests['thread_repeat_8']),
]

xs1_on_tests = [
  XS1Test(on_tests['on_basic'      ], [4, 16, 32, 64]),
  XS1Test(on_tests['on_children'   ], [4]),
  XS1Test(on_tests['on_arguments'  ], [4]),
  XS1Test(on_tests['on_repeat_1'   ], [4, 16]),
  XS1Test(on_tests['on_repeat_loop'], [4, 16]),
  XS1Test(on_tests['on_array'      ], [4, 16, 32, 64]),
  XS1Test(on_tests['on_chain_1'    ], [4, 16, 64]),
  XS1Test(on_tests['on_chain_2'    ], [4, 16, 64]),
  XS1Test(on_tests['on_chain_3'    ], [4, 16, 64]),
  XS1Test(on_tests['on_chain_6'    ], [4, 16, 64]),
  XS1Test(on_tests['on_chain_8'    ], [4, 16, 64]),
  XS1Test(on_tests['on_collision_1'], [4, 16, 64]),
  XS1Test(on_tests['on_collision_2'], [4, 16, 64]),
  XS1Test(on_tests['on_collision_4'], [4, 16, 64]),
]

def run_test(self, name, path, output, num_cores, args=[]):
    """ Run a single test
    """
    try:

        r = call([COMPILE, path+'/'+name+'.sire'] 
                + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, 'a.xe'] + SIM_FLAGS)
        self.assertTrue(r[0])
        self.assertEqual(r[1], output)
    
    except Exception as e:
        sys.stderr.write('Error: {}\n'.format(e))
        raise
    
    except:
        sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
        raise


def test_generator(name, path, output, num_cores):
    """ Generate the test harness
    """
    def test(self):
        run_test(self, name, path, output, num_cores)
    return test

def generate_xs1_example_tests(path):
    """ Dynamically generate all the example tests
    """
    for t in xs1_example_tests:
        for num_cores in t.cores:
            name = 'xs1_test_example_{}_{}c'.format(t.name, num_cores)
            test = test_generator(t.name, path, t.output, num_cores)
            setattr(FeatureTests, name, test)

def generate_xs1_feature_tests(path):
    """ Dynamically generate all the feature tests
    """
    for t in xs1_thread_tests + on_tests:
        for num_cores in t.cores:
            name = 'xs1_test_feature_{}_{}c'.format(t.name, num_cores)
            test = test_generator(t.name, path, t.output, num_cores)
            setattr(FeatureTests, name, test)

