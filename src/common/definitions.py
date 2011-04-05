# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import common.util as util

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
    if lines:
        for x in lines:
            frags = x.split()
            if len(frags) == 3:
                if frags[0] == '#define':
                    s = convert_value(frags[2])
                    globals()[frags[1]] = s
                    #print("Set global {} = {} ({})".format(
                    #    frags[1], s, s.__class__.__name__))
        return True
    else:
        return False

