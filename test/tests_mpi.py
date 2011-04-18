# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import unittest

from util import call
from tests import Test
from tests import ProgramTests
from tests import FeatureTests

COMPILE          = 'sire'
SIMULATE         = 'mpirun'
SIM_FLAGS        = []

class MPITest(Test):
    def __init__(self, test, cores=[1]):
        super(XS1Test, self).__init__(test.name, test.output, test.args)
        self.cores = cores


mpi_example_tests = [ 
  MPITest(example_tests['hello'         ], [1, 4, 16, 32, 64]),
  MPITest(example_tests['factorial-loop']),
  MPITest(example_tests['factorial-rec' ]),
  MPITest(example_tests['fibonacci-loop']),
  MPITest(example_tests['fibonacci-rec' ]),
  MPITest(example_tests['power'         ]),
  MPITest(example_tests['ackermann'     ]),
  MPITest(example_tests['primetest'     ]),
  MPITest(example_tests['bubblesort'    ]),
  MPITest(example_tests['quicksort'     ]),
  MPITest(example_tests['mergesort-seq' ]),
  MPITest(example_tests['mergesort-par' ], [4, 16]),
  MPITest(example_tests['euclid-loop'   ]),
  MPITest(example_tests['euclid-rec'    ]),
  MPITest(example_tests['distribute'    ], [4, 16, 32, 64]),
]
    
mpi_thread_tests = [
  MPITest(thread_tests['thread_basic_2' ]),
  MPITest(thread_tests['thread_basic_4' ]),
  MPITest(thread_tests['thread_basic_8' ]),
  MPITest(thread_tests['thread_repeat_2']),
  MPITest(thread_tests['thread_repeat_8']),
]

mpi_on_tests = [
  MPITest(on_tests['on_basic'      ], [4, 16, 32, 64]),
  MPITest(on_tests['on_children'   ], [4]),
  MPITest(on_tests['on_arguments'  ], [4]),
  MPITest(on_tests['on_repeat_1'   ], [4, 16]),
  MPITest(on_tests['on_repeat_loop'], [4, 16]),
  MPITest(on_tests['on_array'      ], [4, 16, 32, 64]),
  MPITest(on_tests['on_chain_1'    ], [4, 16, 64]),
  MPITest(on_tests['on_chain_2'    ], [4, 16, 64]),
  MPITest(on_tests['on_chain_3'    ], [4, 16, 64]),
  MPITest(on_tests['on_chain_6'    ], [4, 16, 64]),
  MPITest(on_tests['on_chain_8'    ], [4, 16, 64]),
  MPITest(on_tests['on_collision_1'], [4, 16, 64]),
  MPITest(on_tests['on_collision_2'], [4, 16, 64]),
  MPITest(on_tests['on_collision_4'], [4, 16, 64]),
]

def run_test(self, name, path, output, num_cores, args=[]):
    """ Run a single test
    """
    try:

        r = call([COMPILE, path+'/'+name+'.sire'] 
                + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, '-n', '{}'.format(num_cores), 'a.out'] + SIM_FLAGS)
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

def generate_mpi_example_tests(path):
    """ Dynamically generate all the example tests
    """
    for t in mpi_example_tests:
        for num_cores in t.cores:
            name = 'mpi_test_example_{}_{}c'.format(t.name, num_cores)
            test = test_generator(t.name, path, t.output, num_cores)
            setattr(FeatureTests, name, test)

def generate_mpi_feature_tests(path):
    """ Dynamically generate all the feature tests
    """
    for t in mpi_thread_tests + on_tests:
        for num_cores in t.cores:
            name = 'mpi_test_feature_{}_{}c'.format(t.name, num_cores)
            test = test_generator(t.name, path, t.output, num_cores)
            setattr(FeatureTests, name, test)

