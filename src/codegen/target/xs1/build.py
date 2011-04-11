# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import os
import io
import re
import glob
import subprocess
from math import floor

import common.definitions as defs
import common.config as config
import common.util as util
from common.util import verbose_msg
import analysis.builtin as builtin
#from codegen.target.xs1.device import AVAILABLE_XS1_DEVICES

DEVICE_HDR       = 'device.h'
PROGRAM          = 'program'
PROGRAM_SRC      = PROGRAM+'.xc'
PROGRAM_ASM      = PROGRAM+'.S'
PROGRAM_OBJ      = PROGRAM+'.o'
MASTER_JUMPTAB   = 'masterjumptab'
MASTER_TABLES    = 'mastertables'
CONST_POOL       = 'constpool'
MASTER_XE        = 'master.xe'
SLAVE_XE         = 'slave.xe'

XCC              = 'xcc'
XAS              = 'xas'
XOBJDUMP         = 'xobjdump'
COMPILE_FLAGS    = ['-S', '-O0', '-fverbose-asm', '-Wno-timing']
ASSEMBLE_FLAGS   = ['-c', '-O2']
LINK_FLAGS       = ['-nostartfiles', '-Xmapper', '--nochaninit']

RUNTIME_FILES = ['guest.xc', 'host.S', 'host.xc', 'master.S', 'master.xc', 
        'slave.S', 'slave.xc', 'slavetables.S', 'system.S', 'system.xc', 
        'util.xc', 'memory.c']
    
def build_xs1(self, semantics, device, program_buf, outfile, compile_only, 
        verbose=False, showcalls=False):
    """ Run the build process to create either the assembly output or the
        complete binary.
    """
    # Add the include paths once they have been set
    include_dirs = ['-I', config.XS1_RUNTIME_PATH]
    include_dirs += ['-I', config.INCLUDE_PATH]
    include_dirs += ['-I', '.']
    
    global COMPILE_FLAGS
    global ASSEMBLE_FLAGS
    COMPILE_FLAGS += include_dirs
    ASSEMBLE_FLAGS += include_dirs

    if compile_only:
        compile_asm(program_buf, device, outfile)
    else:
        compile_binary(program_buf, device, outfile)

def compile_asm(self, program_buf, device, outfile):
    """ Compile the translated program into assembly.
    """
    
    # Create headers
    s = self.create_headers(device)
    
    # Generate the assembly
    (lines, cp) = self.generate_assembly(program_buf)

    # Write the program back out and assemble
    if s: s = util.write_file(PROGRAM_ASM, ''.join(lines))

    # Rename the output file
    if s: os.rename(PROGRAM_ASM, outfile)
    
    return s

def compile_binary(self, program_buf, device, outfile):
    """ Run the full build
    """
    
    # Create headers
    s = self.create_headers(device)

    # Generate the assembly
    if s: s = self.generate_assembly(program_buf)
    if s: (lines, cp) = s
    #print(''.join(cp))

    # Write the program back out and assemble
    if s: s = self.assemble(PROGRAM, 'S', ''.join(lines))

    # Write the cp out and assemble
    if s: s = self.assemble(CONST_POOL, 'S', ''.join(cp))

    # Output and assemble the master jump and size tables
    if s: 
        buf = io.StringIO()
        self.build_jumptab(buf)
        s = self.assemble(MASTER_JUMPTAB, 'S', buf.getvalue())
    if s: 
        buf = io.StringIO()
        self.build_sizetab(buf)
        self.build_frametab(buf)
        #print(buf.getvalue())
        s = self.assemble(MASTER_TABLES, 'S', buf.getvalue())
    
    # Assemble and link the rest
    if s: s = self.assemble_runtime(device)
    if s: s = self.link_master(device)
    if s: s = self.link_slave(device)
    if s: s = self.replace_slaves()
    
    self.cleanup(outfile)
    return s

def create_headers(self, device):
    self.verbose_msg('Creating device header '+DEVICE_HDR)
    s =  '#define NUM_CORES {}\n'.format(device.num_cores())
    s += '#define NUM_NODES {}\n'.format(device.num_nodes)
    s += '#define NUM_CORES_PER_NODE {}\n'.format(device.num_cores_per_node)
    r = util.write_file(DEVICE_HDR, s)
    return r

def generate_assembly(self, program_buf):
    """ Given the program buffer containing the XC translation, generate the
        program and constant pool assembly.
    """

    # Compile the program into an assembly file
    s = self.compile(PROGRAM, program_buf.getvalue())
    program_buf.close()

    # Read the assembly back in
    if s:
        lines = util.read_file(PROGRAM_ASM, readlines=True)
        s = False if not lines else True

    # Make modifications
    if s: 
        (lines, cp) = self.modify_assembly(lines)
    
    return (lines, cp) if s else None

def compile(self, name, s, cleanup=True):
    """ Compile a buffer containing an XC program
    """
    srcfile = name + '.xc'
    outfile = name + '.S'
    self.verbose_msg('Compiling '+srcfile+' -> '+outfile)
    util.write_file(srcfile, s)
    s = util.call([XCC, srcfile, '-o', outfile] + COMPILE_FLAGS,
            self.showcalls)
    if s and cleanup:
        os.remove(srcfile)
    return s

def assemble(self, name, ext, s, cleanup=True):
    """ Assemble a buffer containing an XC or assembly program
    """
    srcfile = name + '.' + ext
    outfile = name + '.o'
    self.verbose_msg('Assembling '+srcfile+' -> '+outfile)
    util.write_file(srcfile, s)
    if ext == 'xc':
        s = util.call([XCC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS,
                self.showcalls)
    elif ext == 'S':
        s = util.call([XAS, srcfile, '-o', outfile], self.showcalls)
    if s and cleanup: 
        os.remove(srcfile)
    return s

def assemble_runtime(self, device):
    self.verbose_msg('Compiling runtime:')
    s = True
    for x in RUNTIME_FILES:
        objfile = x+'.o'
        self.verbose_msg('  '+x+' -> '+objfile)
        s = util.call([XCC, self.target(device), config.RUNTIME_PATH+'/'+x, 
            '-o', objfile] + ASSEMBLE_FLAGS, self.showcalls)
        if not s: 
            break
    return s

def link_master(self, device):
    """ The jump table must be located at _cp and the common elements of the
        constant and data pools must be in the same positions relative to _cp
        and _dp in the master and slave images.
    """
    self.verbose_msg('Linking master -> '+MASTER_XE)
    s = util.call([XCC, self.target(device), 
        '-first', MASTER_JUMPTAB+'.o', MASTER_TABLES+'.o',
        '-first', CONST_POOL+'.o',
        'system.S.o', 'system.xc.o',
        'guest.xc.o', 'host.xc.o', 'host.S.o',
        'master.xc.o', 'master.S.o',
        'program.o',
        'memory.c.o', 
        'util.xc.o', 
        '-o', MASTER_XE] + LINK_FLAGS,
        self.showcalls)
    return s

def link_slave(self, device):
    """ As above
    """
    self.verbose_msg('Linking slave -> '+SLAVE_XE)
    s = util.call([XCC, self.target(device), 
        '-first', 'slavetables.S.o',
        '-first', CONST_POOL+'.o',
        'system.S.o', 'system.xc.o',
        'guest.xc.o', 'host.xc.o', 'host.S.o',
        'slave.xc.o', 'slave.S.o',
        'memory.c.o', 
        'util.xc.o', 
        '-o', SLAVE_XE] + LINK_FLAGS,
        self.showcalls)
    return s

def replace_slaves(self):
    self.verbose_msg('Replacing master image in node 0, core 0')
    s = util.call([XOBJDUMP, '--split', MASTER_XE], self.showcalls)
    s = util.call([XOBJDUMP, SLAVE_XE, '-r', '0,0,image_n0c0.elf'],
            self.showcalls)
    return s

def modify_assembly(self, lines):
    """ Perform modifications on assembly output
    """
    self.verbose_msg('Modifying assembly output')
    
    #print(''.join(lines))
    (lines, cp) = self.extract_constants(lines)
    lines = self.insert_bottom_labels(lines)
    lines = self.insert_frame_sizes(lines)
    lines = self.rewrite_calls(lines)
    lines.insert(0, '###### MODIFIED ######\n')

    return (lines, cp)

def extract_constants(self, lines):
    """ Extract constant sections only within the elimination block of a
        function. This covers all constants local to a function. This is to
        differentiate constants associated with and declared global.
         - Don't include elimination blocks for strings.
         - Make extracted labels global.
        NOTE: this assumes a constant section will be terminated with a
        .text, (which may not always be true?).
    """
    self.verbose_msg('  Extracting constants')
    cp = []
    new = []
    sect = False
    func = False
    for x in lines:

        # If we have entered a function elimination block
        if re.match(r'\.cc_top [_A-Za-z][A-Za-z0-9_]*\.function', x):
            func = True

        # If we have left
        if re.match(r'\.cc_bottom [_A-Za-z][A-Za-z0-9_]*\.function', x):
            func = False

        if func:

            # If this is a cp section
            if x.find('.section .cp') >= 0:
                sect = True
            
            # If we have left the cp section
            if x.find('.text') >= 0:
                sect = False

            if sect: 
                # If we are in the seciton: replace labels with externs, 
                # declare them as global in the new cp.
                if x.find(':\n') > 0:
                    cp.append('\t.globl '+x[:-2]+'\n')
                    new.insert(0, '\t.extern '+x[:-2]+'\n')
                
                # Rename .const4 and const8 to rodata
                if x.find('.section .cp.const') >= 0:
                    x = '\t.section .cp.rodata, "ac", @progbits\n'

                # Leave .call and .globreads where they are
                if (x.find('.call')!=-1 or x.find('.globread')!=-1):
                    new.append(x)
                # Omit elimination directives (for strings), 
                elif (x.find('.cc_top')==-1 and x.find('.cc_bottom')==-1):
                    cp.append(x)

            # If we're outside a cp section, add to a new list
            else:
                if x.find('.text')==-1:
                    new.append(x)
        
        # If we're outside a function block, add to a new list
        else:
            new.append(x)

    return (new, cp)

def insert_bottom_labels(self, lines):
    """ Insert bottom labels for each function 
    """
    # Look for the structure and insert:
    # > .globl <bottom-label>
    #   foo:
    #     ...
    # > <bottom-label>
    #   .cc_bottom foo.function
    
    self.verbose_msg('  Inserting function labels')
    
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
                if y.split()[0] == '.cc_bottom':
                    new.insert(len(new)-1, 
                            self.function_label_bottom(x)+':\n')
                    b = False
        lines = new

    return lines

def insert_frame_sizes(self, lines):
    """ Insert labels with the value of the size of funciton frames
        (extracted from 'entsp n' instruction)
    """
    self.verbose_msg('  Inserting frame sizes')
        
    b = False
    for x in self.sem.proc_names:
        new = []
        for (i, y) in enumerate(lines):
            new.append(y)
            if b and y.strip()[0:5] == 'entsp':
                size = int(y.strip().split()[1][2:], 16)
                #print(x+' is of size {}'.format(size))
                new.insert(len(new)-1, '.set {}, {}\n'.format(
                    self.function_label_framesize(x), size))
                b = False
            if y == x+':\n':
                new.insert(len(new)-1, '.globl {}\n'.format(
                    self.function_label_framesize(x)))
                b = True          
        lines = new

    return lines

def rewrite_calls(self, lines):
    """ Rewrite calls to program functions to branch through the jump table
    """
    self.verbose_msg('  Rewriting calls')

    for (i, x) in enumerate(lines):
        frags = x.strip().split()
        names = builtin.runtime_functions + self.sem.proc_names 
        if frags and frags[0] == 'bl' and frags[1] in names:
            lines[i] = '\tbla cp[{}]\n'.format(names.index(frags[1]))

    return lines

def build_jumptab(self, buf):

    self.verbose_msg('Building master jump table')
    
    # Constant section
    buf.write('#include "definitions.h"\n')
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
    buf.write('\t.space {}\n'.format(remaining*defs.BYTES_PER_WORD))

def build_sizetab(self, buf):

    self.verbose_msg('Building master size table')
    
    # Data section
    buf.write('\t.section .dp.data, "awd", @progbits\n')
    buf.write('\t.align {}\n'.format(defs.BYTES_PER_WORD))
    
    # Header
    buf.write('\t.globl '+defs.LABEL_SIZE_TABLE+', "a(:ui)"\n')
    buf.write('\t.set {}.globound, {}\n'.format(
        defs.LABEL_SIZE_TABLE, defs.BYTES_PER_WORD*defs.SIZE_TABLE_SIZE))
    buf.write(defs.LABEL_SIZE_TABLE+':\n')
    
    # Pad runtime entries
    for x in range(defs.JUMP_INDEX_OFFSET):
        buf.write('\t.word 0\n')

    # Program procedure entries
    for x in self.sem.proc_names:
        buf.write('\t.word {}-{}+{}\n'.format(
            self.function_label_bottom(x), x, defs.BYTES_PER_WORD))
    
    # Pad any unused space
    remaining = defs.SIZE_TABLE_SIZE - (defs.JUMP_INDEX_OFFSET+
            len(self.sem.proc_names))
    buf.write('\t.space {}\n'.format(remaining*defs.BYTES_PER_WORD))

def build_frametab(self, buf):

    self.verbose_msg('Building master frame table')
    
    # Constant section
    buf.write('\t.section .dp.data, "awd", @progbits\n')
    buf.write('\t.align {}\n'.format(defs.BYTES_PER_WORD))
    
    # Header
    buf.write('\t.globl '+defs.LABEL_FRAME_TABLE+', "a(:ui)"\n')
    buf.write('\t.set {}.globound, {}\n'.format(
        defs.LABEL_FRAME_TABLE, defs.BYTES_PER_WORD*defs.FRAME_TABLE_SIZE))
    buf.write(defs.LABEL_FRAME_TABLE+':\n')
    
    # Pad runtime entries
    for x in range(defs.JUMP_INDEX_OFFSET):
        buf.write('\t.word 0\n')

    # Program procedure entries
    for x in self.sem.proc_names:
        buf.write('\t.word {}\n'.format(self.function_label_framesize(x)))
    
    # Pad any unused space
    remaining = defs.FRAME_TABLE_SIZE - (defs.JUMP_INDEX_OFFSET+
            len(self.sem.proc_names))
    buf.write('\t.space {}\n'.format(remaining*defs.BYTES_PER_WORD))

def cleanup(self, output_xe):
    """ Renanme the output file and delete any temporary files
    """
    self.verbose_msg('Cleaning up')
    
    # Remove specific files
    util.rename_file(SLAVE_XE, output_xe)
    util.remove_file(MASTER_XE)
    util.remove_file('image_n0c0.elf')
    util.remove_file('config.xml')
    util.remove_file('platform_def.xn')
    util.remove_file('program_info.txt')
    util.remove_file(DEVICE_HDR)
    
    # Remove unused master images
    for x in glob.glob('image_n*c*elf'):
        util.remove_file(x)

    # Remove runtime objects
    for x in glob.glob('*.o'):
        util.remove_file(x)

def target(self, device):
    return '{}/{}.xn'.format(config.DEVICE_PATH, device.name)

def function_label_top(self, name):
    return '.'+name+'.top'

def function_label_bottom(self, name):
    return '.'+name+'.bottom'

def function_label_framesize(self, name):
    return '.'+name+'.framesize'

