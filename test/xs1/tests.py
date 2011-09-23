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
D = ['-D'] # Disable all AST transformations

# Examples =====================================================

xs1_example_tests = [ 
  
  # Sequential
  Test('hello', [1, 4, 16, 32, 64], D),
  Test('power',                f=D),
  Test('ackermann',            f=D),
  Test('primetest',            f=D),
  Test('euclid-loop',          f=D),
  Test('euclid-rec',           f=D),
  Test('factorial-loop',       f=D),
  Test('factorial-rec',        f=D),
  Test('fibonacci-loop',       f=D),
  Test('fibonacci-rec',        f=D),
  Test('bubblesort',           f=D),
  Test('quicksort',            f=D),
  Test('mandlebrot-seq',       f=D),
  Test('nqueens-seq',          f=D),
  Test('mergesort-seq',        f=D),
  
  # Parallel (explicit on)
  Test('mergesort-par', [4, 16],         D),
  Test('distribute',    [4, 16, 32, 64], D),

  # Parallel (replicators and channels)
  Test('array1d', [4, 16, 64]),
  Test('array2d', [4],  p=[('N','1')]),
  Test('array2d', [16], p=[('N','2')]),
  Test('array2d', [64], p=[('N','3')]),
  Test('array2d', [64], p=[('N','4')]),
  Test('tree',    [4],  p=[('D','1')]),
  Test('tree',    [16], p=[('D','2')]),
  Test('tree',    [16], p=[('D','3')]),
  Test('tree',    [64], p=[('D','4')]),
  Test('tree',    [64], p=[('D','5')]),
  Test('cube2d',  [4]),
  Test('cube3d',  [16]),
  Test('cube4d',  [64]),
  ]
  
# Features =====================================================

xs1_feature_tests = [

  # Miscellaneous
  Test('assert',        f=D),
  Test('for',           f=D),
  Test('while',         f=D),
  Test('array_elemref', f=D),
  Test('array_alias',   f=D),
  Test('array_slice1',  f=D),
  Test('array_slice2',  f=D),
  
  # Builtins
  Test('builtin_fixedpoint', f=D),
  Test('builtin_printing',   f=D),
  Test('builtin_crc',        f=D),
  Test('builtin_rand',       f=D),
  Test('builtin_procid', [16], D),

  # Threads
  Test('thread_basic_2',     f=D),
  Test('thread_basic_4',     f=D),
  Test('thread_basic_7',     f=D),
  Test('thread_repeat_2',    f=D),
  Test('thread_repeat_7',    f=D),
  Test('thread_arguments_2', f=D),
  Test('thread_arguments_4', f=D),
  Test('thread_arguments_7', f=D),

  # On
  Test('on_self', f=D),
  Test('on_basic',         [4, 16, 32, 64], D),
  Test('on_children',      [4], D),
  Test('on_consecutive',   [4, 16], D),
  Test('on_args_var',      [4, 16, 64], D),
  Test('on_args_array',    [4, 16, 64], D),
  Test('on_args_threaded', [4, 16, 64], D),
  Test('on_squash',        [4, 16, 64], D),
  Test('on_chain_1',       [4, 16, 64], D),
  Test('on_chain_2',       [4, 16, 64], D),
  Test('on_chain_4',       [4, 16, 64], D),
  Test('on_chain_7',       [4, 16, 64], D),
  Test('on_collision_1',   [4, 16, 64], D),
  Test('on_collision_2',   [4, 16, 64], D),
  Test('on_collision_4',   [4, 16, 64], D),

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
  Test('connect_basic',      [4, 16], D),
  Test('connect_reciprocal', [4, 16], D),

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
        p = re.compile('val {} := [0-9]+;'.format(var))
        s = p.sub('val {} := {};'.format(var, value), s, count=1)
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
 
