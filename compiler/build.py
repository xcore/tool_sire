import sys
import os
import io
import util
import glob
import subprocess
import definitions as defs
import config
from math import floor

NUMCORES_HDR   = 'numcores.h'
PROGRAM        = 'program'
PROGRAM_SRC    = PROGRAM+'.xc'
PROGRAM_ASM    = PROGRAM+'.S'
PROGRAM_OBJ    = PROGRAM+'.o'
MASTER_JUMPTAB = 'masterjumptab'
MASTER_SIZETAB = 'mastersizetab'
MASTER_XE      = 'master.xe'
SLAVE_XE       = 'slave.xe'

XCC            = 'xcc'
XAS            = 'xas'
XOBJDUMP       = 'xobjdump'
COMPILE_FLAGS  = ['-S', '-O2']
ASSEMBLE_FLAGS = ['-c', '-O2']
LINK_FLAGS     = ['-nostartfiles', '-Xmapper', '--nochaninit']

RUNTIME_FILES = ['guest.xc', 'host.S', 'host.xc', 'master.S', 'master.xc', 
        'slave.S', 'slavejumptab.S', 'system.S', 'system.xc', 'util.xc']

class Build(object):
    """ A class to compile, assemble and link the program source with the
        runtime into an executable multi-core binary.
    """
    def __init__(self, numcores, semantics, verbose=False):
        self.numcores = numcores
        self.sem = semantics
        self.verbose = verbose

    def run(self, program_buf, outfile):
        """ Run the full build
        """
        # Output the master jump and size tables
        jumptab_buf = io.StringIO()
        sizetab_buf = io.StringIO()
        self.build_jumptab(jumptab_buf)
        self.build_sizetab(sizetab_buf)
        
        self.create_headers()
        s = self.compile_buf(PROGRAM, program_buf)
        if s: 
            program_buf.close()
            program_buf = io.StringIO()
            s = self.insert_labels(PROGRAM_ASM, program_buf)
        if s: s = self.assemble_buf(PROGRAM, 'S', program_buf)
        if s: s = self.assemble_buf(MASTER_JUMPTAB, 'S', jumptab_buf)
        if s: s = self.assemble_buf(MASTER_SIZETAB, 'S', sizetab_buf)
        if s: s = self.assemble_runtime()
        if s: s = self.link_master()
        if s: s = self.link_slave()
        if s: s = self.replace_slaves()
        self.cleanup(outfile)
        return s

    def compile(self, buf, outfile):
        """ Compile the program only
        """
        s = True
        s = self.compile_buf(PROGRAM, buf)
        buf.close()
        buf = io.StringIO()
        self.insert_labels(PROGRAM_ASM, buf)
        if s: s = util.write_file(PROGRAM_ASM, buf.getvalue())
        os.rename(PROGRAM_ASM, outfile)
        return s

    def create_headers(self):
        # TODO: shouldn't really write to this directory...
        self.verbose_msg('Creating header '+NUMCORES_HDR)
        util.write_file(config.INCLUDE_PATH+'/'+NUMCORES_HDR, 
                '#define NUM_CORES {}'.format(self.numcores));

    def compile_buf(self, name, buf, cleanup=True):
        """ Compile a buffer containing an XC program
        """
        srcfile = name + '.xc'
        outfile = name + '.S'
        self.verbose_msg('Compiling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        s = util.call([XCC, srcfile, '-o', outfile] + COMPILE_FLAGS)
        if cleanup:
            os.remove(srcfile)
        return s

    def assemble_buf(self, name, ext, buf, cleanup=True):
        """ Assemble a buffer containing an XC or assembly program
        """
        srcfile = name + '.' + ext
        outfile = name + '.o'
        self.verbose_msg('Assembling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        if ext == 'xc':
            s = util.call([XCC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS)
        elif ext == 'S':
            s = util.call([XAS, srcfile, '-o', outfile])
        if cleanup: 
            os.remove(srcfile)
        return s

    def assemble_runtime(self):
        self.verbose_msg('Compiling runtime:')
        s = True
        for x in RUNTIME_FILES:
            objfile = x+'.o'
            self.verbose_msg('  '+x+' -> '+objfile)
            s = util.call([XCC, self.target(), config.RUNTIME_PATH+'/'+x, '-o', objfile] 
                    + ASSEMBLE_FLAGS)
        return s

    def link_master(self):
        self.verbose_msg('Linking master -> '+MASTER_XE)
        s = util.call([XCC, self.target(), 
            '-first '+MASTER_JUMPTAB+'.o', MASTER_SIZETAB+'.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'master.xc.o', 'master.S.o', 
            'program.o',
            'util.xc.o', '-o', MASTER_XE] + LINK_FLAGS)
        return s

    def link_slave(self):
        self.verbose_msg('Linking slave -> '+SLAVE_XE)
        s = util.call([XCC, self.target(), 
            '-first slavejumptab.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'slave.S.o',
            'util.xc.o', '-o', SLAVE_XE] + LINK_FLAGS)
        return s

    def replace_slaves(self):
        self.verbose_msg('Splitting slave')
        s = util.call([XOBJDUMP, '--split', SLAVE_XE])
        self.verbose_msg('\r  Replacing node 0, core', end='')
        for x in range(1, self.numcores):
            node = floor(x / defs.CORES_PER_NODE)
            core = floor(x % defs.CORES_PER_NODE)
            if core == 0:
                self.verbose_msg('\r  Replacing node {}, core 0'.format(node),
                        end='')
            else:
                self.verbose_msg(' {}'.format(core), end='')
            s = util.call([XOBJDUMP, MASTER_XE, 
                    '-r', '{},{},image_n0c0.elf'.format(node, core)])
        self.verbose_msg('')
        return s

    def insert_labels(self, file, buf):
        """ Insert top and bottom labels for each function 
        """
        # Look for the structure and insert:
        # > .globl <bottom-label>
        #   foo:
        #     ...
        # > <bottom-label>
        #   .cc_bottom foo.function
        
        self.verbose_msg('Inserting function labels in '+file)
        lines = util.read_file(file, readlines=True)
        if not lines:
            return False

        # For each function, for each line...
        # (Create a new list and modify it each time...)
        b = False
        for x in self.sem.proc_names:
            new = []
            for (i, y) in enumerate(lines):
                new.append(y)
                if y == x+':\n' and not b:
                    new.insert(len(new)-1, 
                            '.globl '+self.function_label_bottom(x)+'\n')
                    b = True
                elif y[0] == '.' and b:
                    if y.split(' ')[0] == '.cc_bottom':
                        new.insert(len(new)-1, 
                                self.function_label_bottom(x)+':\n')
                        b = False
            lines = new
    
        # Make sure the buffer is empty and write the lines
        for x in lines:
            buf.write(x)

        return True

    def build_jumptab(self, buf):

        self.verbose_msg('Building master jump table')
        
        # Constant section
        buf.write('\t.section .cp.rodata, "ac", @progbits\n')
        buf.write('\t.align {}\n'.format(defs.BYTES_PER_WORD))
        
        # Header
        buf.write('\t.globl '+defs.LABEL_JUMP_TABLE+', "a(:ui)"\n')
        buf.write('\t.set {}.globound, {}\n'.format(
            defs.LABEL_JUMP_TABLE, defs.BYTES_PER_WORD*defs.JUMP_TABLE_SIZE))
        buf.write(defs.LABEL_JUMP_TABLE+':\n')
        
        # Runtime entries
        buf.write('\t.word '+defs.LABEL_MIGRATE+'\n')
        buf.write('\t.word '+defs.LABEL_INIT_THREAD+'\n')
        buf.write('\t.word '+defs.LABEL_CONNECT+'\n')

        # Program entries
        for x in self.sem.proc_names:
            buf.write('\t.word '+x+'\n')

        # Pad any unused space
        remaining = defs.JUMP_TABLE_SIZE - (defs.JUMP_INDEX_OFFSET+
                len(self.sem.proc_names))
        buf.write('\t.space {}\n'.format(remaining))

    def build_sizetab(self, buf):

        self.verbose_msg('Building master size table')
        
        # Data section
        buf.write('\t.section .dp.data, "awd", @progbits\n')
        buf.write('\t.align {}\n'.format(defs.BYTES_PER_WORD))
        
        # Header
        buf.write('\t.globl '+defs.LABEL_SIZE_TABLE+'\n')
        buf.write('\t.set {}.globound, {}\n'.format(
            defs.LABEL_SIZE_TABLE,
            defs.BYTES_PER_WORD*(defs.JUMP_INDEX_OFFSET+
                len(self.sem.proc_names))))
        buf.write(defs.LABEL_SIZE_TABLE+':\n')
        
        # Pad runtime entries
        for x in range(defs.JUMP_INDEX_OFFSET):
            buf.write('\t.word 0\n')

        # Program procedure entries
        for x in self.sem.proc_names:
            buf.write('\t.word {}-{}+{}\n'.format(
                self.function_label_bottom(x), x, defs.BYTES_PER_WORD))

    def cleanup(self, output_xe):
        """ Renanme the output file and delete any temporary files
        """
        self.verbose_msg('Cleaning up')
        util.rename_file(MASTER_XE, output_xe)
        util.remove_file('image_n0c0.elf')
        util.remove_file('config.xml')
        util.remove_file('platform_def.xn')
        util.remove_file('program_info.txt')
        util.remove_file('slave.xe')
        for x in glob.glob('*.o'):
            util.remove_file(x)

    def target(self):
        return '{}/XMP-{}.xn'.format(config.DEVICE_PATH, self.numcores)

    def function_label_top(self, name):
        return '.L'+name+'_top'

    def function_label_bottom(self, name):
        return '.L'+name+'_bottom'

    def verbose_msg(self, msg, end='\n'):
        if self.verbose: 
            sys.stdout.write(msg+end)
            sys.stdout.flush()

