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
SIM_FLAGS = ['-s']
#SIMULATE = 'xsim'
#SIM_FLAGS = ['--no-warn-registers']
D = ['-D'] # Disable all AST transformations

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
  Test('fibonacci-rec', f=D),
  Test('bubblesort'),
  Test('quicksort', f=D),
  Test('mandlebrot-seq'),
  Test('nqueens-seq', f=D),
  Test('mergesort-seq', f=D),
  
  # Parallel and recursive (explicit on)
  Test('mergesort-par', [4, 16], f=D),
  Test('distribute',    [4, 16, 32, 64], f=D),

  # Parallel (replicators and channels)
  Test('array1d',           [4, 16, 64]),
  Test('array1d_composite', [4, 16]),
  Test('array2d',           [4],  p=[('N','2')]),
  Test('array2d_composite', [4],  p=[('N','1')]),
  Test('array2d_composite', [16], p=[('N','2')]),
  Test('tree',              [4],  p=[('D','1')]),
  Test('tree',              [16], p=[('D','2')]),
  Test('quadtree',          [22]),
  Test('cube2d',            [4]),
  Test('cube3d',            [16]),
  Test('distributed-array', [5],  p=[('N', '4')]),
  Test('farm',              [16], p=[('N', '16')]),

  # These exceed 8 threads on some nodes.
  #Test('array2d',           [16], p=[('N','4')]),
  #Test('array2d_composite', [64], p=[('N','3')]),
  #Test('array2d_composite', [64], p=[('N','4')]),
  #Test('tree',              [16], p=[('D','3')]), 
  #Test('tree',              [64], p=[('D','4')]), 
  #Test('tree',              [64], p=[('D','5')]), 
  #Test('cube4d',            [64]),
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
  Test('builtin_fileio'),
  Test('builtin_comm', [16]),
  Test('builtin_remotemem', [4], f=D),
  Test('builtin_mem'),
  Test('builtin_crc'),
  Test('builtin_time'),
  Test('builtin_rand'),
  Test('builtin_procid', [16]),

  # Threads
  Test('thread_basic_2'),
  Test('thread_basic_4'),
  Test('thread_basic_7'),
  Test('thread_repeat_2'),
  Test('thread_repeat_7'),
  Test('thread_arguments_2'),
  Test('thread_arguments_4'),
  Test('thread_arguments_7'),

  # On
  Test('on_self'),
  Test('on_basic',         [4, 16, 32, 64]),
  Test('on_children',      [4]),
  Test('on_consecutive',   [4, 16]),
  Test('on_args_var',      [4, 16, 64]),
  Test('on_args_array',    [4, 16, 64]),
  Test('on_args_threaded', [4, 16, 64]),
  Test('on_squash',        [4, 16, 64]),
  Test('on_chain_1',       [4, 16, 64]),
  Test('on_chain_2',       [4, 16, 64]),
  Test('on_chain_4',       [4, 16, 64]),
  Test('on_chain_7',       [4, 16, 64]),
  Test('on_collision_1',   [4, 16, 64]),
  Test('on_collision_2',   [4, 16, 64]),
  Test('on_collision_4',   [4, 16, 64]),

  # Replicators
  Test('rep_basic_1d', [4, 16, 32, 64]),
  Test('rep_basic_2d', [4],  p=[('X','1'), ('Y','1')]),
  Test('rep_basic_2d', [4],  p=[('X','2'), ('Y','2')]),
  Test('rep_basic_2d', [16], p=[('X','3'), ('Y','3')]),
  Test('rep_basic_2d', [64], p=[('X','8'), ('Y','8')]),
  Test('rep_basic_3d', [16], p=[('X','1'), ('Y','1'), ('Z','1')]),
  Test('rep_basic_3d', [16], p=[('X','2'), ('Y','2'), ('Z','2')]),
  Test('rep_basic_3d', [64], p=[('X','3'), ('Y','3'), ('Z','3')]),
  Test('rep_basic_3d', [64], p=[('X','4'), ('Y','4'), ('Z','4')]),
  Test('rep_basic_4d', [4],  p=[('W','1'), ('X','1'), ('Y','1'), ('Z','1')]),
  Test('rep_basic_4d', [16], p=[('W','2'), ('X','2'), ('Y','2'), ('Z','2')]),
  Test('rep_basic_4d', [64], p=[('W','2'), ('X','4'), ('Y','2'), ('Z','4')]),

  # Connect
  Test('connect_basic',      [4, 16], f=D),
  Test('connect_reciprocal', [4, 16], f=D),

  # Server
  Test('server_1', [4]),
  Test('server_2', [4]),
  Test('server_3', [4]),
  Test('server_4', [16]),
  Test('server_5', [16]),
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
        p = re.compile('val {} is [0-9]+;'.format(var))
        s = p.sub('val {} is {};'.format(var, value), s, count=1)
      filename = os.getcwd()+'/'+name+'.sire.tmp'
      write_file(filename, s) 

    # Compile the program
    (exit, output) = call([COMPILE, filename]
        + ['-t', 'XS1', '-n', '{}'.format(num_cores)] + cmp_flags)
    self.assertTrue(exit)

    # Delete the temporary version
    if len(param) > 0:
      remove_file(filename)

    # Simulate execution
    (exit, output) = call([SIMULATE, 'a.se'] + SIM_FLAGS)
    self.assertTrue(exit)

    # Check the output against the .output file
    self.assertEqual(output.strip(), 
        read_file(path+'/'+name+'.output').strip())
  
  except Exception as e:
    sys.stderr.write('Error: {}\n'.format(e))
    raise

def generate_xs1_example_tests(path):
  return generate_test_set('xs1', path, xs1_example_tests, run_test)
  
def generate_xs1_feature_tests(path):
  return generate_test_set('xs1', path, xs1_feature_tests, run_test)
 
