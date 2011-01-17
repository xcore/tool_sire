import sys
import re
import subprocess

def read_file(filename, readlines=False):
    """ Read a file and return its contents as a string 
    """
    #verbose_report("Reading input file '{}'...\n".format(filename))
    contents=None
    try:
        file = open(filename, 'r')
        if readlines:
            contents = file.readlines()
        else:
            contents = file.read()
        file.close()
    except IOError as err:
        print('Error reading input ({}): {}'.format(err.errno, err.strerror),
                file=sys.stderr)
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])
    return contents

def write_file(filename, s):
    """ Write the output to a file 
    """
    #verbose_report("Writing output file '{}'...\n".format(filename))
    try:
        file = open(filename, 'w')
        file.write(s)
        file.close()
    except IOError as err:
        print('Error writing output ({}): {}'.format(err.errno, err.strerror),
                file=sys.stderr)
    except:
        raise Exception('Unexpected error:', sys.exc_info()[0])

def call(args):
    """ Try to execute a shell command
    """
    try:
        s = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('Error executing command: {}\nOuput: {}'.format(
            err.cmd, err.output))
        return True
    return False

def camel_to_under(s):
    return re.sub("([A-Z])([A-Z][a-z])|([a-z0-9])([A-Z])", 
            lambda m: '{}_{}'.format(m.group(3), m.group(4)), s).lower()

def indexed_dict(elements):
    return dict([(e,i) for i, e in list(enumerate(elements))])

