import util

#SYS_CORE_ARRAY = 'core'
#SYS_CHAN_ARRAY = 'chan'
#LABEL_MAIN        = '_main'
#LABEL_MIGRATE     = 'migrate'
#LABEL_INIT_THREAD = 'initThread'
#LABEL_CONNECT     = 'connect'

def convert_value(s):
    """ Convert a string value from a #define
    """

    # If its a string
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    # If its a decimal number
    elif s.isnumeric():
        return int(s)
    # If its hexdecimal
    elif s[:2] == '0x':
        return int(s[2:], 16)
    else:
        return s

def load(filename):
    lines = util.read_file(filename, readlines=True)
    for x in lines:
        frags = x.split()
        if len(frags) == 3:
            if frags[0] == '#define':
                s = convert_value(frags[2])
                globals()[frags[1]] = s
                #print("Set global {} = {} ({})".format(
                #    frags[1], s, s.__class__.__name__))

