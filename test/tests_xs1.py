# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import unittest

from util import call
from tests import Test
from tests import TestSet
from tests import example_tests
from tests import thread_tests
from tests import on_tests

COMPILE          = 'sire'
SIMULATE         = 'xsim'

xs1_example_tests = [ 
  TestSet(example_tests['hello'         ], [1, 4, 16, 32, 64]),
  TestSet(example_tests['factorial-loop']),
  TestSet(example_tests['factorial-rec' ]),
  TestSet(example_tests['fibonacci-loop']),
  TestSet(example_tests['fibonacci-rec' ]),
  TestSet(example_tests['power'         ]),
  TestSet(example_tests['ackermann'     ]),
  TestSet(example_tests['primetest'     ]),
  TestSet(example_tests['bubblesort'    ]),
  TestSet(example_tests['quicksort'     ]),
  TestSet(example_tests['mergesort-seq' ]),
  TestSet(example_tests['mergesort-par' ], [4, 16]),
  TestSet(example_tests['euclid-loop'   ]),
  TestSet(example_tests['euclid-rec'    ]),
  TestSet(example_tests['distribute'    ], [4, 16, 32, 64]),
  ]
    
xs1_thread_tests = [
  TestSet(thread_tests['thread_basic_2' ]),
  TestSet(thread_tests['thread_basic_4' ]),
  TestSet(thread_tests['thread_basic_8' ]),
  TestSet(thread_tests['thread_repeat_2']),
  TestSet(thread_tests['thread_repeat_8']),
  ]

xs1_on_tests = [
  TestSet(on_tests['on_basic'      ], [4, 16, 32, 64]),
  TestSet(on_tests['on_children'   ], [4]),
  TestSet(on_tests['on_arguments'  ], [4]),
  TestSet(on_tests['on_repeat_1'   ], [4, 16]),
  TestSet(on_tests['on_repeat_loop'], [4, 16]),
  TestSet(on_tests['on_array'      ], [4, 16, 32, 64]),
  TestSet(on_tests['on_chain_1'    ], [4, 16, 64]),
  TestSet(on_tests['on_chain_2'    ], [4, 16, 64]),
  TestSet(on_tests['on_chain_3'    ], [4, 16, 64]),
  TestSet(on_tests['on_chain_6'    ], [4, 16, 64]),
  TestSet(on_tests['on_chain_8'    ], [4, 16, 64]),
  TestSet(on_tests['on_collision_1'], [4, 16, 64]),
  TestSet(on_tests['on_collision_2'], [4, 16, 64]),
  TestSet(on_tests['on_collision_4'], [4, 16, 64]),
  ]

def run_test(self, name, path, output, num_cores, args=[]):
    """ Run a single test
    """
    try:
        r = call([COMPILE, path+'/'+name+'.sire'] 
                + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, 'a.xe'])
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

def generate_xs1_tests(category, path):
    """ Dynamically generate all the example tests
    """
    if category == 'example':
        test_set = xs1_example_tests
    elif category == 'feature':
        test_set = xs1_feature_tests
    
    tests = []
    for t in test_set:
        for num_cores in t.cores:
            name = 'test_xs1_{}_{}_{}c'.format(category, t.name, num_cores)
            test = test_generator(t.name, path, t.output, num_cores)
            test.__name__ = name
            tests.append(test)

    return tests

