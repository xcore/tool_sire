import sys
import subprocess

def call(args):
    """ Execute a shell command, return (success, output)
    """
    try:
    
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

