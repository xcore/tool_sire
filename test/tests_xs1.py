# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import unittest

from util import call
from util import read_file
from tests import Test
from tests import generate_test_set

COMPILE  = 'sire'
SIMULATE = 'xsim'
SIM_FLAGS = []

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
  Test('mergesort-par', [4, 16]),
  Test('distribute', [4, 16, 32, 64]),
  ]
    
# Features =====================================================

xs1_feature_general = [
  Test('for'),
  Test('array_elemref'),
  Test('array_alias'),
  Test('array_slice1'),
  Test('array_slice2'),
  ]

xs1_feature_builtins = [
  Test('builtin_fixedpoint'),
  Test('builtin_printing'),
  Test('builtin_procid', [16]),
  ]

xs1_feature_thread = [
  Test('thread_basic_2'),
  Test('thread_basic_4'),
  Test('thread_basic_8'),
  Test('thread_repeat_2'),
  Test('thread_repeat_8'),
  ]

xs1_feature_on = [
  Test('on_self'),
  Test('on_basic',       [4, 16, 32, 64]),
  Test('on_children',    [4]),
  Test('on_arguments',   [4]),
  Test('on_repeat_1',    [4, 16]),
  Test('on_repeat_loop', [4, 16]),
  Test('on_array',       [4, 16, 32, 64]),
  Test('on_chain_1',     [4, 16, 64]),
  Test('on_chain_2',     [4, 16, 64]),
  Test('on_chain_3',     [4, 16, 64]),
  Test('on_chain_6',     [4, 16, 64]),
  Test('on_chain_8',     [4, 16, 64]),
  Test('on_collision_1', [4, 16, 64]),
  Test('on_collision_2', [4, 16, 64]),
  Test('on_collision_4', [4, 16, 64]),
  ] 

xs1_feature_replicator = [
  Test('rep_basic_1d',   [4, 16, 32, 64]),
  Test('rep_basic_2d',   [4, 16, 32, 64]),
  Test('rep_basic_3d',   [4, 16, 32, 64]),
  ]

xs1_feature_tests =\
  xs1_feature_general\
  + xs1_feature_builtins\
  + xs1_feature_thread\
  + xs1_feature_on 
  #+ xs1_feature_replicator

def run_test(self, name, path, num_cores, args=[]):
    """
    Run a single test.
    """
    try:

        # Compile the program
        (exit, output) = call([COMPILE, path+'/'+name+'.sire'] 
                + ['-t', 'xs1', '-n', '{}'.format(num_cores)] + args)
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
    
