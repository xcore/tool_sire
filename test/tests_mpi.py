# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import unittest

from util import call
from tests import Test
from tests import TestSet
from tests import generate_test_set

# Test sets
from tests import examples
from tests import feature_general
from tests import feature_thread
from tests import feature_on
from tests import feature_replicator

COMPILE  = 'sire'
SIMULATE = 'mpirun'
SIM_FLAGS = ['-q']

# Examples =====================================================

mpi_example_tests = [ 
  TestSet(examples['hello'         ]),
  TestSet(examples['factorial-loop']),
  TestSet(examples['factorial-rec' ]),
  TestSet(examples['fibonacci-loop']),
  TestSet(examples['fibonacci-rec' ]),
  TestSet(examples['power'         ]),
  TestSet(examples['ackermann'     ]),
  TestSet(examples['primetest'     ]),
  TestSet(examples['bubblesort'    ]),
  TestSet(examples['quicksort'     ]),
  TestSet(examples['euclid-loop'   ]),
  TestSet(examples['euclid-rec'    ]),
  TestSet(examples['mergesort-seq' ]),
  #TestSet(examples['mergesort-par' ], [4, 16]),
  #TestSet(examples['distribute'    ], [4, 16, 32, 64]),
  ]

# Features =====================================================

mpi_feature_general = [
  #TestSet(feature_general['array']),
  #TestSet(feature_general['for']),
  ]

mpi_feature_thread = [
  #TestSet(feature_thread['thread_basic_2' ]),
  #TestSet(feature_thread['thread_basic_4' ]),
  #TestSet(feature_thread['thread_basic_8' ]),
  #TestSet(feature_thread['thread_repeat_2']),
  #TestSet(feature_thread['thread_repeat_8']),
  ] 

mpi_feature_on = [
  #TestSet(feature_on['on_basic'      ], [4, 16, 32, 64]),
  #TestSet(feature_on['on_children'   ], [4]),
  #TestSet(feature_on['on_arguments'  ], [4]),
  #TestSet(feature_on['on_repeat_1'   ], [4, 16]),
  #TestSet(feature_on['on_repeat_loop'], [4, 16]),
  #TestSet(feature_on['on_array'      ], [4, 16, 32, 64]),
  #TestSet(feature_on['on_chain_1'    ], [4, 16, 64]),
  #TestSet(feature_on['on_chain_2'    ], [4, 16, 64]),
  #TestSet(feature_on['on_chain_3'    ], [4, 16, 64]),
  #TestSet(feature_on['on_chain_6'    ], [4, 16, 64]),
  #TestSet(feature_on['on_chain_8'    ], [4, 16, 64]),
  #TestSet(feature_on['on_collision_1'], [4, 16, 64]),
  #TestSet(feature_on['on_collision_2'], [4, 16, 64]),
  #TestSet(feature_on['on_collision_4'], [4, 16, 64]),
  ] 

mpi_feature_replicator = [
  ]

mpi_feature_tests =\
  mpi_feature_general +\
  mpi_feature_thread +\
  mpi_feature_on +\
  mpi_feature_replicator

def run_test(self, name, path, output, num_cores, args=[]):
    """ Run a single test
    """
    try:
        r = call([COMPILE, path+'/'+name+'.sire'] 
                + ['-t', 'mpi', '-n', '{}'.format(num_cores)] + args)
        self.assertTrue(r[0])
        r = call([SIMULATE, '-np', '{}'.format(num_cores), 'a.out'] + SIM_FLAGS)
        self.assertTrue(r[0])
        # Compare output string (stripping first line).
        self.assertEqual(r[1], output)
    
    except Exception as e:
        sys.stderr.write('Error: {}\n'.format(e))
        raise
    
    except:
        sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
        raise

def generate_mpi_example_tests(path):
    return generate_test_set('mpi', path, mpi_example_tests, run_test)
    
def generate_mpi_feature_tests(path):
    return generate_test_set('mpi', path, mpi_feature_tests, run_test)
    
