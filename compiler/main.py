import sys
import lexer
import parser

# Open file specified
if len(sys.argv) == 2:
    try:
        input = open(sys.argv[1]).read()
    except IOError, (errno, stderror):
        print "I/O error({0}): {1}".format(errno, stderror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    input.close()
    prog = parser.parse(input)
    #if not prog raise SystemExit
    print prog
