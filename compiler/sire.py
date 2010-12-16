import sys
sys.path.insert(0,"../..")

import lexer
import parser

from ply import *

if len(sys.argv) == 1:
    print "Usage: sire.py <input-file>"
    raise SystemExit

# Set up a logging object
import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

# Open file specified
if len(sys.argv) == 2:
    try:
        file = open(sys.argv[1])
        input = file.read()
    except IOError, (errno, stderror):
        print "I/O error({0}): {1}".format(errno, stderror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    file.close()
    log = logging.getLogger()
    prog = parser.parse(input,debug=log)
#    prog = parser.parse(input)
#    print prog
    #if not prog raise SystemExit
