# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import unittest
import re
import os

from util import call
from util import read_file
from util import write_file
from util import remove_file
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
  
  # Sequential
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
  
  # Parallel (explicit on)
  Test('mergesort-par', [4, 16],         NO_DIST),
  Test('distribute',    [4, 16, 32, 64], NO_DIST),

  # Parallel (replicators and channels)
  Test('array1d', [4, 16, 64]),
  Test('array2d', [4],  param=[('N','1')]),
  Test('array2d', [16], param=[('N','2')]),
  Test('array2d', [64], param=[('N','3')]),
  Test('array2d', [64], param=[('N','4')]),
  Test('tree',    [4],  param=[('D','1')]),
  Test('tree',    [16], param=[('D','2')]),
  Test('tree',    [16], param=[('D','3')]),
  Test('tree',    [64], param=[('D','4')]),
  Test('tree',    [64], param=[('D','5')]),
  Test('cube2d',  [4]),
  Test('cube3d',  [16]),
  Test('cube4d',  [64]),
  ]
  
# Features =====================================================

xs1_feature_tests = [

  # Miscellaneous
  Test('assert'),
  Test('for'),
  Test('while'),
  Test('array_elemref'),
  Test('array_alias'),
  Test('array_slice1'),
  Test('array_slice2'),
  
  # Builtins
  Test('builtin_fixedpoint'),
  Test('builtin_printing'),
  Test('builtin_procid', [16]),

  # Threads
  Test('thread_basic_2',     [1], NO_DIST),
  Test('thread_basic_4',     [1], NO_DIST),
  Test('thread_basic_7',     [1], NO_DIST),
  Test('thread_repeat_2',    [1], NO_DIST),
  Test('thread_repeat_7',    [1], NO_DIST),
  Test('thread_arguments_2', [1], NO_DIST),
  Test('thread_arguments_4', [1], NO_DIST),
  Test('thread_arguments_7', [1], NO_DIST),

  # On
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

  # Replicators
  Test('rep_basic_1d', [4, 16, 32, 64]),
  Test('rep_basic_2d', [4],  param=[('X','1'), ('Y','1')]),
  Test('rep_basic_2d', [4],  param=[('X','2'), ('Y','2')]),
  Test('rep_basic_2d', [16], param=[('X','3'), ('Y','3')]),
  Test('rep_basic_2d', [64], param=[('X','8'), ('Y','8')]),
  Test('rep_basic_3d', [16], param=[('X','1'), ('Y','1'), ('Z','1')]),
  Test('rep_basic_3d', [16], param=[('X','2'), ('Y','2'), ('Z','2')]),
  Test('rep_basic_3d', [64], param=[('X','3'), ('Y','3'), ('Z','3')]),
  Test('rep_basic_3d', [64], param=[('X','4'), ('Y','4'), ('Z','4')]),
  Test('rep_basic_4d', [4],  param=[('W','1'), ('X','1'), ('Y','1'), ('Z','1')]),
  Test('rep_basic_4d', [16], param=[('W','2'), ('X','2'), ('Y','2'), ('Z','2')]),
  Test('rep_basic_4d', [64], param=[('W','2'), ('X','4'), ('Y','2'), ('Z','4')]),

  # Connect
  Test('connect_basic',      [4, 16], NO_DIST),
  Test('connect_reciprocal', [4, 16], NO_DIST),
  ]

def run_test(self, name, path, num_cores, cmp_flags, param):
  """
  Run a single test.
  """
  try:

    filename = path+'/'+name+'.sire'

    # Substitute parameters in a new temporary file
    if len(param) > 0:
      s = read_file(filename)
      for (var, value) in param:
        p = re.compile('val {} := [0-9]+;'.format(var))
        s = p.sub('val {} := {};'.format(var, value), s, count=1)
      filename = os.getcwd()+'/'+name+'.sire.tmp'
      write_file(filename, s) 

    # Compile the program
    (exit, output) = call([COMPILE, filename]
        + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + cmp_flags)
    self.assertTrue(exit)

    # Delete the temporary version
    if len(param) > 0:
      remove_file(filename)

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
 
