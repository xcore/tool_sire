import sys
import glob
import os
import util
import subprocess
from math import floor

RUNTIME_DIR    = 'runtime'
INCLUDE_DIR    = 'include'
CONFIGS_DIR    = 'configs'
NUMCORES_HDR   = 'numcores.h'
PROGRAM_SRC    = 'program.xc'
PROGRAM_ASM    = 'program.S'
PROGRAM_OBJ    = 'program.o'
MASTER_XE      = 'master.xe'
SLAVE_XE       = 'slave.xe'

XCC            = 'xcc'
XOBJDUMP       = 'xobjdump'
COMPILE_FLAGS  = ['-S', '-O3']
ASSEMBLE_FLAGS = ['-c', '-O3']
LINK_FLAGS     = ['-nostartfiles', '-Xmapper', '--nochaninit']

CORES_PER_NODE = 4

RUNTIME_FILES = ['guest.xc', 'host.S', 'host.xc', 'master.S', 'master.xc', 
'slave.S', 'slavetable.S', 'system.S', 'system.xc', 'util.xc']

class Build(object):
    """ A class to compile, assemble and link the program source with the
        runtime into an executable multi-core binary.
    """
    def __init__(self, numcores, verbose=False):
        self.numcores = numcores
        self.verbose = verbose

    def run(self, program_buf, jumptab_buf, sizetab_buf):
        """ Run the full build
        """
        e = False
        self.create_headers()
        if not e: e = self.assemble_buf('program', 'xc', program_buf)
        if not e: e = self.assemble_buf('jumptab', 'S',  jumptab_buf)
        if not e: e = self.assemble_buf('sizetab', 'S',  sizetab_buf)
        if not e: e = self.assemble_runtime()
        if not e: e = self.link_master()
        if not e: e = self.link_slave()
        if not e: e = self.replace_slaves()
        self.cleanup()

    def compile(self, program_buf):
        """ Compile the program only
        """
        self.compile_buf('program', program_buf)

    def create_headers(self):
        self.verbose_msg('Creating header '+NUMCORES_HDR)
        util.write_file(INCLUDE_DIR+'/'+NUMCORES_HDR, 
                '#define NUM_CORES {}'.format(self.numcores));

    def compile_buf(self, name, buf):
        """ Compile a buffer containing an XC program """
        srcfile = name + '.xc'
        outfile = name + '.S'
        self.verbose_msg('Compiling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        e = self.call([XCC, srcfile, '-o', outfile] + COMPILE_FLAGS)
        os.remove(srcfile)
        return e

    def assemble_buf(self, name, ext, buf):
        """ Assemble a buffer containing an XC or assembly program """
        srcfile = name + '.' + ext
        outfile = name + '.o'
        self.verbose_msg('Assembling '+srcfile+' -> '+outfile)
        util.write_file(srcfile, buf.getvalue())
        e = self.call([XCC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS)
        #os.remove(srcfile)
        return e

    def target(self):
        return '{}/XMP-{}.xn'.format(CONFIGS_DIR, self.numcores)

    def assemble_runtime(self):
        self.verbose_msg('Compiling runtime:')
        #files = glob.glob(RUNTIME_DIR+'/*.xc')
        #files += glob.glob(RUNTIME_DIR+'/*.S')
        e = False
        for x in RUNTIME_FILES:
            objfile = x+'.o'
            self.verbose_msg('  '+x+' -> '+objfile)
            e = self.call([XCC, self.target(), RUNTIME_DIR+'/'+x, '-o', objfile] 
                    + ASSEMBLE_FLAGS)
        return e

    def link_master(self):
        self.verbose_msg('Linking master')
        e = self.call([XCC, self.target(), 
            '-first mastertable.o', 'sizetab.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'master.xc.o', 'master.S.o', 
            'program.o',
            'util.xc.o', '-o '+MASTER_XE] + LINK_FLAGS)
        return e

    def link_slave(self):
        self.verbose_msg('Linking slave')
        e = self.call([XCC, self.target(), 
            '-first slavetable.o',
            'system.S.o', 'system.xc.o',
            'guest.xc.o', 'host.xc.o', 'host.S.o',
            'slave.xc.o',
            'util.xc.o', '-o '+SLAVE_XE] + LINK_FLAGS)
        return e

    def replace_slaves(self):
        self.verbose_msg('Splitting slave')
        e = self.call([XOBJDUMP, '--split', SLAVE_XE, '>/dev/null'])
        for x in range(self.numcores):
            node = floor(x / CORES_PER_NODE)
            core = floor(x % CORES_PER_NODE)
            if core == 0:
                self.verbose_msg('  Replacing node {}, core 0'.format(node))
            else:
                self.verbose_msg('{}'.format(core))
            e = self.call([XOBJDUMP], MASTER_XE, 
                    '-r {},{},image_n0c0.elf'.format(node, core),
                    '> /dev/null')
        return e

    def cleanup(self):
        self.verbose_msg('Cleaning up')
        #os.remove('*.o')

    def call(self, args):
        """ Try to execute a shell command
        """
        try:
            s = subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print('Error executing command: {}\nOuput: {}'.format(
                err.cmd, err.output))
            return True
        return False

    def verbose_msg(self, msg):
        if self.verbose: 
            sys.stdout.write(msg+'\n')

