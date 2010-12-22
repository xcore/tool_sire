import sys
sys.path.insert(0,"../..")

from parser import Parser

from ply import *
import show

# Set up a logging object
import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

if len(sys.argv) == 1:
    print "Usage: sire.py <input-file>"
    raise SystemExit

# Open file specified
elif len(sys.argv) == 2:
    try:
        filename = sys.argv[1]
        file = open(filename)
        input = file.read()
    except IOError, (errno, stderror):
        print "I/O error({0}): {1}".format(errno, stderror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    file.close()

    log = logging.getLogger()
    parser = Parser(lex_optimise=True, yacc_debug=False, yacc_optimise=False)
    prog = parser.parse(input, filename, debug=0)
    prog.accept(show.Show())
