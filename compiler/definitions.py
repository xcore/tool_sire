import util

#SYS_CORE_ARRAY = 'core'
#SYS_CHAN_ARRAY = 'chan'
#LABEL_MAIN        = '_main'
#LABEL_MIGRATE     = 'migrate'
#LABEL_INIT_THREAD = 'initThread'
#LABEL_CONNECT     = 'connect'

def load(filename):
    lines = util.read_file(filename, readlines=True)
    for x in lines:
        frags = x.split()
        if len(frags) == 3:
            if frags[0] == '#define':
                globals()[frags[1]] = frags[2]
                #print("Set global {} = {}".format(frags[1], frags[2]))

