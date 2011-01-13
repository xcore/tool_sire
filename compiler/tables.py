# TODO: read all these from definitions fil
# TODO: fix top and bottom function labels

JUMP_TABLE = 'jumpTable'
SIZE_TABLE = 'sizeTable'
NUM_RUNTIME_ENTRIES = 3
JUMP_TABLE_SIZE = 10
BYTES_PER_WORD = 4

LBL_MIGRATE     = 'migrate'
LBL_INIT_THREAD = 'initThread'
LBL_CONNECT     = 'connect'

def function_label_bottom(name):
    return 'topof_'+name

def function_label_top(name):
    return 'bottomof_'+name

def build_jumptab(buf, proc_names):

    # Constant section
    buf.write('\t.section .cp.rodata, "ac", @progbits\n')
    buf.write('\t.align {}\n'.format(BYTES_PER_WORD))
    
    # Header
    buf.write('\t.globl '+JUMP_TABLE+', "a(:ui)"\n')
    buf.write('\t.set {}.globound, {}\n'.format(JUMP_TABLE,
        BYTES_PER_WORD*JUMP_TABLE_SIZE))
    buf.write(JUMP_TABLE+':\n')
    
    # Runtime entries
    buf.write('\t.word '+LBL_MIGRATE+'\n')
    buf.write('\t.word '+LBL_INIT_THREAD+'\n')
    buf.write('\t.word '+LBL_CONNECT+'\n')

    # Program entries
    for x in proc_names:
        buf.write('\t.word '+x+'\n')

    # Pad any unused space
    remaining = JUMP_TABLE_SIZE - (NUM_RUNTIME_ENTRIES+len(proc_names))
    buf.write('\t.space {}\n'.format(remaining))

def build_sizetab(buf, proc_names):

    # Data section
    buf.write('\t.section .dp.data, "awd", @progbits\n')
    buf.write('\t.align {}\n'.format(BYTES_PER_WORD))
    
    # Header
    buf.write('\t.globl '+SIZE_TABLE+'\n')
    buf.write('\t.set {}.globound, {}\n'.format(SIZE_TABLE,
        BYTES_PER_WORD*(NUM_RUNTIME_ENTRIES+len(proc_names))))
    buf.write(SIZE_TABLE+':\n')
    
    # Pad runtime entries
    for x in range(NUM_RUNTIME_ENTRIES):
        buf.write('\t.word 0\n')

    # Program procedure entries
    for x in proc_names:
        buf.write('\t.word {}-{}+{}\n'.format(
            function_label_bottom(x), function_label_top(x), BYTES_PER_WORD))

