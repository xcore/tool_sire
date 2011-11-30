# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import re
import os
import subprocess
from math import log, ceil
from error import Error

def read_file(filename, read_lines=False):
  """ 
  Read a file and return its contents as a string. 
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
    raise Error('Error reading input {}: {}'
        .format(filename, err.strerror))
  except:
    raise Exception('Unexpected error: {}'
        .format(sys.exc_info()[0]))

def write_file(filename, s):
  """ 
  Write the output to a file.
  """
  try:
  
    file = open(filename, 'w')
    file.write(s)
    file.close()
    return True
  except IOError as err:
    sys.stderr.write('writing output {}: {}'
        .format(filename, err.strerror))
    raise Error()
  except:
    raise Exception('Unexpected error: {}'
        .format(sys.exc_info()[0]))

def call(args, verbose=False, display_stdout=True):
  """ 
  Try to execute a shell command.
  """
  try:
    if verbose:
      print(' '.join(args))
    s = subprocess.check_output(args, stderr=subprocess.STDOUT)
    if display_stdout:
      sys.stdout.write(s.decode("utf-8").replace("\\n", "\n"))
  
  except subprocess.CalledProcessError as e:
    s = e.output.decode('utf-8').replace("\\n", "\n")
    #sys.stderr.write('\nCall error: '+s)
    #sys.stderr.write(' '.join(args)+'\n')
    sys.stderr.write('executing command:\n\n{}\n\nOuput:\n\n{}'
        .format(' '.join(e.cmd), s))
    raise Error()
  
  except:
    #sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
    raise Exception('Unexpected error: {}'.format(sys.exc_info()[0]))

def remove_file(filename):
  """ 
  Remove a file if it exists.
  """
  if os.path.isfile(filename):
    os.remove(filename)

def rename_file(filename, newname):
  """ 
  Rename a file if it exists.
  """
  if os.path.isfile(filename):
    os.rename(filename, newname)

def camel_to_under(s):
  """ 
  Covert a camel-case string to use underscores.
  """
  return re.sub("([A-Z])([A-Z][a-z])|([a-z0-9])([A-Z])", 
      lambda m: '{}_{}'.format(m.group(3), m.group(4)), s).lower()

def indexed_dict(elements):
  """ 
  Return a dictionary of indexes for item keys.
  """
  return dict([(e,i) for i, e in list(enumerate(elements))])
  
def vhdr(verbose, msg, end='\n'):
  """
  Verbose header: output a message that is displayed in verbose mode.
  """
  if verbose: 
    sys.stdout.write('-'*len(str(msg))+'\n')
    sys.stdout.write(msg+end)
    sys.stdout.write('-'*len(str(msg))+'\n')
    sys.stdout.flush()
  
def next_power_of_2(n):
  return (2 ** ceil(log(n, 2)))

def vmsg(verbose, msg, end='\n'):
  """ 
  Verbose message: output a message that is displayed in verbose mode.
  """
  if verbose: 
    sys.stdout.write(msg+end)
    sys.stdout.flush()

def debug(display, msg):
  if display:
    print(msg)

