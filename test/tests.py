# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import unittest

INSTALL_PATH_ENV = 'SIRE_INSTALL_PATH'
EXAMPLES_DIR     = '/test/examples-old' 
FEATURES_DIR     = '/test/features' 

class Test(object):
    def __init__(self, name, output, cores=[1], args=[]):
        self.name = name
        self.output = output
        self.cores = cores
        self.args = args

class ProgramTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

class FeatureTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

# Examples =====================================================

example_tests = { 
  'hello'          : Test('hello',          'hello world\n'),
  'factorial-loop' : Test('factorial-loop', '6\n120\n5040\n'),
  'factorial-rec'  : Test('factorial-rec',  '6\n120\n5040\n'),
  'fibonacci-loop' : Test('fibonacci-loop', '8\n89\n987\n'),
  'fibonacci-rec'  : Test('fibonacci-rec',  '8\n89\n987\n'),
  'power'          : Test('power',          '32\n729\n78125\n'),
  'ackermann'      : Test('ackermann',      '3\n11\n29\n'),
  'primetest'      : Test('primetest',      '1010101000101000101000100\n'),
  'bubblesort'     : Test('bubblesort',     '0123456789\n'),
  'quicksort'      : Test('quicksort',      '0123456789\n'),
  'mergesort-seq'  : Test('mergesort-seq',  '0123456789\n'),
  'mergesort-par'  : Test('mergesort-par',  '0123456789101112131415\n'),
  'euclid-loop'    : Test('euclid-loop',    '8\n7\n1\n'),
  'euclid-rec'     : Test('euclid-rec',     '8\n7\n1\n'),
  'distribute'     : Test('distribute',     ''),
  }

# Features =====================================================

array_tests = {
  }

for_tests = {
  }

on_tests = {
  'on_basic'       : Test('on_basic',       'DEADBEEF\n'),
  'on_children'    : Test('on_children',    'DEADBEEF\n'),
  'on_arguments'   : Test('on_arguments',   '28\n21\n41\n'),
  'on_repeat_1'    : Test('on_repeat_1',    'DEADBEEF\n'),
  'on_repeat_loop' : Test('on_repeat_loop', 'DEADBEEF\n'),
  'on_array'       : Test('on_array',       'DEADBEEF\n'),
  'on_chain_1'     : Test('on_chain_1',     ''),
  'on_chain_2'     : Test('on_chain_2',     ''),
  'on_chain_3'     : Test('on_chain_3',     ''),
  'on_chain_6'     : Test('on_chain_6',     ''),
  'on_chain_8'     : Test('on_chain_8',     ''),
  'on_collision_1' : Test('on_collision_1', ''),
  'on_collision_2' : Test('on_collision_2', ''),
  'on_collision_4' : Test('on_collision_4', ''),
  }

thread_tests = {
  'thread_basic_2'  : Test('thread_basic_2',  ''),
  'thread_basic_4'  : Test('thread_basic_4',  ''),
  'thread_basic_8'  : Test('thread_basic_8',  ''),
  'thread_repeat_2' : Test('thread_repeat_2', ''),
  'thread_repeat_8' : Test('thread_repeat_8', ''),
  }

replicator_tests = {
  }

