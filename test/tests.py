# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from util import read_file

class Test(object):
    """ A generic test object with a list (of system sizes) for specific tests.
    """
    def __init__(self, test, cores=[1]):
        self.test = test
        self.cores = cores


def test_generator(name, path, output, num_cores, run_test):
    """ Generate the test harness
    """
    def test(self):
        run_test(self, name, path, output, num_cores)
    return test

def generate_test_set(target, path, test_set, run_test):
    tests = []
    for t in test_set:
        for num_cores in t.cores:
            name = 'test_{}_{}_{}c'.format(
                    target, t.test.name, num_cores)
            test = test_generator(t.test.name, path, t.test.output, 
                        num_cores, run_test)
            test.__name__ = name
            tests.append(test)
    return tests

