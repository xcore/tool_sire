import sys
import subprocess
import os

def test_generator(name, path, num_cores, cmp_flags, param, run_test):
  """ 
  Generate the test harness.
  """
  def test(self):
    run_test(self, name, path, num_cores, cmp_flags, param)
  return test

def generate_test_set(target, path, test_set, run_test):
  """
  Given a test set generate the unit test methods.
  """
  tests = []
  for t in test_set:
    for num_cores in t.cores:
      name = 'test_{}_{}_{}c'.format(target, t.name, num_cores)
      test = test_generator(t.name, path, num_cores, 
          t.cmp_flags, t.param, run_test)
      test.__name__ = name
      tests.append(test)
  return tests

def read_file(filename, read_lines=False):
  """ 
  Read a file and return its contents as a string 
  """
  try:
    #print('reading '+filename)
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
    sys.stderr.write('Error writing output {}: {}'
        .format(filename, err.strerror))
    raise Error()

def remove_file(filename):
  """ 
  Remove a file if it exists.
  """
  if os.path.isfile(filename):
    os.remove(filename)

def call(args):
  """ 
  Execute a shell command, return (success, output)
  """
  try:
    #print(' '.join(args))
    s = subprocess.check_output(args, stderr=subprocess.STDOUT)
    return (1, s.decode('utf-8'))

  # If return value non-zero.
  except subprocess.CalledProcessError as err:
    s = err.output.decode('utf-8').replace("\\n", "\n")
    sys.stderr.write('\nCall error: '+s)
    sys.stderr.write(' '.join(args)+'\n')
    return (0, None)

