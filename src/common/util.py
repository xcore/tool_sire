# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import re
import os
import subprocess

def read_file(filename, read_lines=False):
    """ Read a file and return its contents as a string 
    """
    try:
        contents=None
        file = open(filename, 'r')
        if read_lines:
            contents = file.readlines()
        else:
            contents = file.read()
        file.close()
        return contents
    except IOError as err:
        raise Error('Error reading input ({}): {}'
                .format(err.errno, err.strerror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])

def write_file(filename, s):
    """ Write the output to a file 
    """
    try:
        file = open(filename, 'w')
        file.write(s)
        file.close()
        return True
    except IOError as err:
        raise Error('writing output ({}): {}'
                .format(err.errno, err.strerror))
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])

def call(args, verbose=False):
    """ Try to execute a shell command
    """
    try:
        if verbose:
            print(' '.join(args))
        s = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        s = err.output.decode('utf-8').replace("\\n", "\n")
        raise Error('executing command:\n\n{}\n\nouput:\n\n{}'
                .format(' '.join(err.cmd), s))

def remove_file(filename):
    """ Remove a file if it exists
    """
    if os.path.isfile(filename):
        os.remove(filename)

def rename_file(filename, newname):
    """ Rename a file if it exists
    """
    if os.path.isfile(filename):
        os.rename(filename, newname)

def camel_to_under(s):
    """ Covert a camel-case string to use underscores 
    """
    return re.sub("([A-Z])([A-Z][a-z])|([a-z0-9])([A-Z])", 
            lambda m: '{}_{}'.format(m.group(3), m.group(4)), s).lower()

def indexed_dict(elements):
    """ Return a dictionary of indexes for item keys 
    """
    return dict([(e,i) for i, e in list(enumerate(elements))])
    
def vmsg(verbose, msg, end='\n'):
    """ Output a message that is displayed in verbose mode.
    """
    if verbose: 
        sys.stdout.write(msg+end)
        sys.stdout.flush()

