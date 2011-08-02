# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import unittest

from util import call
from util import read_file
from util import generate_test_set
from test import Test

COMPILE  = 'sire'
SIMULATE = 'axe'
SIM_FLAGS = []
#SIMULATE = 'xsim'
#SIM_FLAGS = ['--no-warn-registers']
NO_DIST = ['-D']

# Examples =====================================================

xs1_example_tests = [ 
  Test('hello', [1, 4, 16, 32, 64]),
  Test('power'),
  Test('ackermann'),
  Test('primetest'),
  Test('euclid-loop'),
  Test('euclid-rec'),
  Test('factorial-loop'),
  Test('factorial-rec'),
  Test('fibonacci-loop'),
  Test('fibonacci-rec'),
  Test('bubblesort'),
  Test('quicksort'),
  Test('mandlebrot-seq'),
  Test('nqueens-seq'),
  Test('mergesort-seq'),
  Test('mergesort-par', [4, 16],         NO_DIST),
  Test('distribute',    [4, 16, 32, 64], NO_DIST),
  ]
  
# Features =====================================================

xs1_feature_tests = [
  Test('assert'),
  Test('for'),
  Test('while'),
  Test('array_elemref'),
  Test('array_alias'),
  Test('array_slice1'),
  Test('array_slice2'),
  
  Test('builtin_fixedpoint'),
  Test('builtin_printing'),
  Test('builtin_procid', [16]),

  Test('thread_basic_2',     NO_DIST),
  Test('thread_basic_4',     NO_DIST),
  Test('thread_basic_7',     NO_DIST),
  Test('thread_repeat_2',    NO_DIST),
  Test('thread_repeat_7',    NO_DIST),
  Test('thread_arguments_2', NO_DIST),
  Test('thread_arguments_4', NO_DIST),
  Test('thread_arguments_7', NO_DIST),

  Test('on_self'),
  Test('on_basic',         [4, 16, 32, 64]),
  Test('on_children',      [4]),
  Test('on_consecutive',   [4, 16]),
  Test('on_args_var',      [4, 16, 64]),
  Test('on_args_array',    [4, 16, 64]),
  Test('on_args_threaded', [4, 16, 64], NO_DIST),
  Test('on_squash',        [4, 16, 64], NO_DIST),
  Test('on_chain_1',       [4, 16, 64], NO_DIST),
  Test('on_chain_2',       [4, 16, 64], NO_DIST),
  Test('on_chain_4',       [4, 16, 64], NO_DIST),
  Test('on_chain_7',       [4, 16, 64], NO_DIST),
  Test('on_collision_1',   [4, 16, 64], NO_DIST),
  Test('on_collision_2',   [4, 16, 64], NO_DIST),
  Test('on_collision_4',   [4, 16, 64], NO_DIST),

  Test('rep_basic_1d', [4, 16, 32, 64]),
  Test('rep_basic_2d', [4, 16, 32, 64]),
  Test('rep_basic_3d', [16, 32, 64]),

  Test('connect_basic',      [4, 16], NO_DIST),
  Test('connect_reciprocal', [4, 16], NO_DIST),
  ]

def run_test(self, name, path, num_cores, cmp_flags):
  """
  Run a single test.
  """
  try:

    # Compile the program
    (exit, output) = call([COMPILE, path+'/'+name+'.sire'] 
        + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + cmp_flags)
    self.assertTrue(exit)

    # Simulate execution
    (exit, output) = call([SIMULATE, 'a.xe'] + SIM_FLAGS)
    self.assertTrue(exit)

    # Check the output against the .output file
    self.assertEqual(output.strip(), 
        read_file(path+'/'+name+'.output').strip())
  
  except Exception as e:
    sys.stderr.write('Error: {}\n'.format(e))
    raise
  
  except:
    sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
    raise

def generate_xs1_example_tests(path):
  return generate_test_set('xs1', path, xs1_example_tests, run_test)
  
def generate_xs1_feature_tests(path):
  return generate_test_set('xs1', path, xs1_feature_tests, run_test)
 
