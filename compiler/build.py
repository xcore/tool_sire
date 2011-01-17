import sys
import os
import io
import util
import subprocess
import assembly
from math import floor

RUNTIME_DIR    = 'runtime'
INCLUDE_DIR    = 'include'
CONFIGS_DIR    = 'configs'
NUMCORES_HDR   = 'numcores.h'
PROGRAM        = 'program'
PROGRAM_SRC    = 'program.xc'
PROGRAM_ASM    = 'program.S'
PROGRAM_OBJ    = 'program.o'
MASTER_JUMPTAB = 'masterjumptab'
MASTER_SIZETAB = 'mastersizetab'
MASTER_XE      = 'master.xe'
SLAVE_XE       = 'slave.xe'

XCC            = 'xcc'
XOBJDUMP       = 'xobjdump'
COMPILE_FLAGS  = ['-S', '-O2']
ASSEMBLE_FLAGS = ['-c', '-O2']
LINK_FLAGS     = ['-nostartfiles', '-Xmapper', '--nochaninit']

CORES_PER_NODE = 4

RUNTIME_FILES = ['guest.xc', 'host.S', 'host.xc', 'master.S', 'master.xc', 
'slave.S', 'slavejumptab.S', 'system.S', 'system.xc', 'util.xc']

JUMP_TABLE = 'jumpTable'
SIZE_TABLE = 'sizeTable'
NUM_RUNTIME_ENTRIES = 3
JUMP_TABLE_SIZE = 10
BYTES_PER_WORD = 4

# TODO: read all these from definitions fil
# TODO: fix top and bottom function labels

LBL_MIGRATE     = 'migrate'
LBL_INIT_THREAD = 'initThread'
LBL_CONNECT     = 'connect'

class Build(object):
    """ A class to compile, assemble and link the program source with the
        runtime into an executable multi-core binary.
    """
    def __init__(self, numcores, semantics, verbose=False):
        self.numcores = numcores
        self.sem = semantics
        self.verbose = verbose

    def run(self, program_buf):
        """ Run the full build
        """
        e = False

        # Output the master jump and size tables
        jumptab_buf = io.StringIO()
        sizetab_buf = io.StringIO()
        self.build_jumptab(jumptab_buf)
        self.build_sizetab(sizetab_buf)
        
        self.create_headers()
        if not e: e = self.compile_buf(PROGRAM, program_buf, False)
        if not e: 
            program_buf.close()
            program_buf = io.StringIO()
            self.extract_asm(PROGRAM_ASM, program_buf)
        if not e: self.assemble_buf(PROGRAM, 'S', program_buf, False)
        if not e: e = self.assemble_buf(MASTER_JUMPTAB, 'S', jumptab_buf)
        if not e: e = self.assemble_buf(MASTER_SIZETAB, 'S', sizetab_buf)
        if not e: e = self.assemble_runtime()
        if not e: e = self.link_master()
        #if not e: e = self.link_slave()
        #if not e: e = self.replace_slaves()
        self.cleanup()

    def compile(self, program_buf):
        """ Compile the program only
        """
        self.compile_buf('program', program_buf)

    def create_headers(self):
        self.verbose_msg('Creating header '+NUMCORES_HDR)
        util.write_file(INCLUDE_DIR+'/'+NUMCORES_HDR, 
                '#define NUM_CORES {}'.format(self.numcores));

    def compile_buf(self, name, buf, cleanup=True):
        """ Compile a buffer containing an XC program """
        srcfile = name + '.xc'
        outfile = name + '.S'
        self.verbose_msg('Compiling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        e = util.call([XCC, srcfile, '-o', outfile] + COMPILE_FLAGS)
        if cleanup:
            os.remove(srcfile)
        return e

    def assemble_buf(self, name, ext, buf, cleanup=True):
        """ Assemble a buffer containing an XC or assembly program """
        srcfile = name + '.' + ext
        outfile = name + '.o'
        self.verbose_msg('Assembling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        e = util.call([XCC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS)
        if cleanup: 
            os.remove(srcfile)
        return e

    def target(self):
        return '{}/XMP-{}.xn'.format(CONFIGS_DIR, self.numcores)

    def assemble_runtime(self):
        self.verbose_msg('Compiling runtime:')
        e = False
        for x in RUNTIME_FILES:
            objfile = x+'.o'
            self.verbose_msg('  '+x+' -> '+objfile)
            e = util.call([XCC, self.target(), RUNTIME_DIR+'/'+x, '-o', objfile] 
                    + ASSEMBLE_FLAGS)
        return e

    def link_master(self):
        self.verbose_msg('Linking master')
        e = util.call([XCC, self.target(), 
            '-first '+MASTER_JUMPTAB+'.o', MASTER_SIZETAB+'.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'master.xc.o', 'master.S.o', 
            'program.o',
            'util.xc.o', '-o '+MASTER_XE] + LINK_FLAGS)
        return e

    def link_slave(self):
        self.verbose_msg('Linking slave')
        e = util.call([XCC, self.target(), 
            '-first slavejumptab.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'slave.xc.o',
            'util.xc.o', '-o '+SLAVE_XE] + LINK_FLAGS)
        return e

    def replace_slaves(self):
        self.verbose_msg('Splitting slave')
        e = util.call([XOBJDUMP, '--split', SLAVE_XE, '>/dev/null'])
        for x in range(self.numcores):
            node = floor(x / CORES_PER_NODE)
            core = floor(x % CORES_PER_NODE)
            if core == 0:
                self.verbose_msg('  Replacing node {}, core 0'.format(node))
            else:
                self.verbose_msg('{}'.format(core))
            e = util.call([XOBJDUMP], MASTER_XE, 
                    '-r {},{},image_n0c0.elf'.format(node, core),
                    '> /dev/null')
        return e

    def extract_asm(self, file, buf):
        """ Extact relevant sections from generated assembly file """
        # *Assume function definitions will come first
        
        self.verbose_msg('Extracting assembly sections')
        lines = util.read_file(file, readlines=True)
        externs = []
        functions = {}
        current = None

        # For each line of assembly
        for x in lines:
            if x[0] == '.':
                frags = x.split(' ')
                directive = frags[0]
                if directive == '.extern':
                    externs.append(x)
                elif directive == '.cc_top':
                    name = frags[1].split('.')[0]
                    if not name in functions:
                        functions[name] = []
                    current = name if len(functions[name])==0 else None
                elif directive == '.cc_bottom':
                    name = frags[1].split('.')[0]
                    if current: 
                        functions[name].append(x)
                    current = None
            
            if current:
                functions[current].append(x)

        # Write a new assembly file in buf
        for x in externs:
            buf.write(x)
        
        buf.write('\t.text\n')
        for x in self.sem.proc_names:
            buf.write(self.function_label_top(x)+':\n')
            for y in functions[x]:
                buf.write(y)
            buf.write(self.function_label_bottom(x)+':\n')

        #print(buf.getvalue())

    def build_jumptab(self, buf):

        self.verbose_msg('Building master jump table')
        
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
        for x in self.sem.proc_names:
            buf.write('\t.word '+x+'\n')

        # Pad any unused space
        remaining = JUMP_TABLE_SIZE - (NUM_RUNTIME_ENTRIES+
                len(self.sem.proc_names))
        buf.write('\t.space {}\n'.format(remaining))

    def build_sizetab(self, buf):

        self.verbose_msg('Building master size table')
        
        # Data section
        buf.write('\t.section .dp.data, "awd", @progbits\n')
        buf.write('\t.align {}\n'.format(BYTES_PER_WORD))
        
        # Header
        buf.write('\t.globl '+SIZE_TABLE+'\n')
        buf.write('\t.set {}.globound, {}\n'.format(SIZE_TABLE,
            BYTES_PER_WORD*(NUM_RUNTIME_ENTRIES+
                len(self.sem.proc_names))))
        buf.write(SIZE_TABLE+':\n')
        
        # Pad runtime entries
        for x in range(NUM_RUNTIME_ENTRIES):
            buf.write('\t.word 0\n')

        # Program procedure entries
        for x in self.sem.proc_names:
            buf.write('\t.word {}-{}+{}\n'.format(
                self.function_label_bottom(x), 
                self.function_label_top(x), 
                BYTES_PER_WORD))

    def function_label_top(self, name):
        return '.Ltop_'+name

    def function_label_bottom(self, name):
        return '.Lbottom_'+name

    def cleanup(self):
        self.verbose_msg('Cleaning up')

    def verbose_msg(self, msg):
        if self.verbose: 
            sys.stdout.write(msg+'\n')

