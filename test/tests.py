#!/usr/bin/env python3.1

import subprocess
import unittest

SIRE = '../compiler/sire.py'
XSIM = 'xsim'
PROGRAM_DIR = 'programs/'

class Test(unittest.TestCase):

    def call(self, args):
        """ Execute a shell command
        """
        try:
            s = subprocess.check_output(args, stderr=subprocess.STDOUT)
            return s.decode('utf-8')
        except subprocess.CalledProcessError as err:
            s = err.output.decode('utf-8').replace("\\n", "\n")
            print('Error executing command:\n{}\nOuput:\n{}'.format(err.cmd, s))
            return None

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        s = self.call([SIRE, PROGRAM_DIR+'hello.sire'])
        self.assertTrue(not s)
        s = self.call([XSIM, 'a.xe'])
        self.assertEqual(s, 'hello world\n')

if __name__ == '__main__':
    unittest.main()
