import sys
import subprocess

def test_generator(name, path, num_cores, run_test):
  """ 
  Generate the test harness.
  """
  def test(self):
    run_test(self, name, path, num_cores)
  return test

def generate_test_set(target, path, test_set, run_test):
  tests = []
  for t in test_set:
    for num_cores in t.cores:
      name = 'test_{}_{}_{}c'.format(target, t.name, num_cores)
      test = test_generator(t.name, path, num_cores, run_test)
      test.__name__ = name
      tests.append(test)
  return tests

def read_file(filename, read_lines=False):
  """ Read a file and return its contents as a string 
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
  except:
    raise Exception('Unexpected error: {}'
        .format(sys.exc_info()[0]))

def call(args):
  """ Execute a shell command, return (success, output)
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

  except:
    sys.stderr.write("Unexpected error: {}\n".format(sys.exc_info()[0]))
    return (0, None)

