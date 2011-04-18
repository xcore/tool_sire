import subprocess

def call(args):
    """ Execute a shell command, return (success, output)
    """
    try:
        # Returning non-zero will riase CalledProcessError
        s = subprocess.check_output(args, stderr=subprocess.STDOUT)
        return s.decode('utf-8')
    except subprocess.CalledProcessError as err:
        s = err.output.decode('utf-8').replace("\\n", "\n")
        raise Exception('Error executing command:\n{}\nOuput:\n{}'.format(err.cmd, s))

