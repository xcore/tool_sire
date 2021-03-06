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
import struct
import math

import definitions as defs
import config
import util
from util import vmsg
from error import Error
import builtin
from target.definitions import *

DEVICE_HDR    = 'device.h'
PROGRAM       = 'program'
PROGRAM_SRC   = PROGRAM+'.xc'
PROGRAM_ASM   = PROGRAM+'.S'
PROGRAM_OBJ   = PROGRAM+'.o'
MASTER_TABLES = 'masterTables'
CONST_POOL    = 'constpool'
MASTER_XE     = 'master.xe'
SLAVE_XE      = 'slave.xe'
FINAL_XE      = 'a.xe'

XCC             = 'xcc'
XAS             = 'xas'
XOBJDUMP        = 'xobjdump'
# NOTE: Ignore warnings when compiling program source
COMPILE_FLAGS = ['-S', '-O2', #'-fllvm', 
  '-Wall', '-Wextra', 
  #'-fverbose-asm', '-Winline','-Wno-timing',  '-Wunreachable-code',
  ]
ASSEMBLE_FLAGS = ['-c', '-O2', #'-fllvm',
  '-Wall', '-Wextra', 
  #'-fverbose-asm', '-Winline', '-Wno-timing',  '-Wunreachable-code',
  ]
LINK_FLAGS = ['-nostartfiles', '-Xmapper', '--nochaninit']

RUNTIME_FILES = [
  'source.xc', 
  'host.S', 
  'host.xc', 
  'connect.xc', 
  'master.S', 
  'master.xc', 
  'slave.S', 
  'globals.S',
  'system.S', 
  'system.xc', 
  'control.xc',
  'worker.xc',
  'util.xc', 
  'memory.c',
  'pointer.c',
  ]
  
def build_xs1(sig, device, program_buf, outfile, 
    compile_only, display_memory, 
    show_calls=False, save_temps=False, v=False):
  """ 
  Run the build process to create either the assembly output or the complete
  binary.
  """
  # Add the include paths once they have been set
  include_dirs = ['-I', '.']
  include_dirs += ['-I', config.INSTALL_PATH]
  
  global COMPILE_FLAGS
  global ASSEMBLE_FLAGS
  COMPILE_FLAGS += include_dirs
  ASSEMBLE_FLAGS += include_dirs

  # Try to run the build, pass any Error or SystemExit exceptions along to
  # main driver after having cleaned up and temporary files.
  try:

    # Create headers
    create_headers(device, v)

    # Generate the assembly
    (lines, cp) = generate_assembly(sig, program_buf, show_calls, v, save_temps)

    if compile_only:
      
      # Write the program back out and assemble
      util.write_file(PROGRAM_ASM, ''.join(lines))

      # Rename the output file
      outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
          outfile+'.'+device.assembly_file_ext())
      os.rename(PROGRAM_ASM, outfile)

      raise SystemExit() 

    # Write the program back out and assemble
    assemble_str(PROGRAM, 'S', ''.join(lines), show_calls, v)

    # Write the cp out and assemble
    assemble_str(CONST_POOL, 'S', ''.join(cp), show_calls, v)

    # Output and assemble the master jump table
    buf = io.StringIO()
    build_master_tab_init(sig, buf, v)
    #print(buf.getvalue())
    assemble_str(MASTER_TABLES, 'S', buf.getvalue(), show_calls, v, save_temps)

    # Assemble and link the rest
    assemble_runtime(device, show_calls, v)
    link_master(device, show_calls, v)
    link_slave(device, show_calls, v)
    replace_images(show_calls, v)
    
    # Dump memory usage information
    if display_memory:
      dump_memory_use()

    # Append XE to header in output file
    outfile = (outfile if outfile!=defs.DEFAULT_OUT_FILE else
        outfile+'.se')
    append_header(device, outfile, show_calls, v)
    vmsg(v, 'Produced file: '+outfile)

  except Error as e:
    raise Error(e.args)
  
  except SystemExit:
    raise SystemExit()
  
  except:
    raise
    
  finally:
    if not save_temps:
      cleanup(v)

def create_headers(device, v):
  vmsg(v, 'Creating device header '+DEVICE_HDR)
  s =  '#define NUM_CORES {}\n'.format(device.num_cores())
  s += '#define NUM_CORES_LOG {}\n'.format(
      int(math.log(device.num_cores())/math.log(2)))
  s += '#define NUM_CORES_SQRT {}\n'.format(
      int(math.sqrt(device.num_cores())))
  s += '#define NUM_NODES 0\n'
  s += '#define NUM_CORES_PER_NODE NUM_CORES\n'
  s += '#define XS1_L\n'
  #s += '#define NUM_NODES {}\n'.format(device.num_nodes)
  #s += '#define NUM_CORES_PER_NODE {}\n'.format(device.num_cores_per_node)
  #if device.type == XS1_DEVICE_TYPE_G:
  #  s +=  '#define XS1_G\n'
  #elif device.type == XS1_DEVICE_TYPE_L:
  #  s +=  '#define XS1_L\n'
  util.write_file(DEVICE_HDR, s)

def generate_assembly(sig, buf, show_calls, v, save_temps):
  """ 
  Given the program buffer containing the XC translation, generate the program
  and constant pool assembly.
  """

  # Compile the program into an assembly file
  compile_str(PROGRAM, buf.getvalue(), show_calls, v, save_temps)
  buf.close()

  # Read the assembly back in
  lines = util.read_file(PROGRAM_ASM, read_lines=True)

  # Make modifications
  (lines, cp) = modify_assembly(sig, lines, v)
  
  return (lines, cp)

def compile_str(name, string, show_calls, v, save_temps=True):
  """ 
  Compile a buffer containing an XC program.
  """
  srcfile = name + '.xc'
  outfile = name + '.S'
  vmsg(v, 'Compiling '+srcfile+' -> '+outfile)
  util.write_file(srcfile, string)
  util.call([XCC, srcfile, '-o', outfile] + COMPILE_FLAGS, v=show_calls)
  if not save_temps:
    os.remove(srcfile)

def assemble_str(name, ext, string, show_calls, v, save_temps=False):
  """ 
  Assemble a buffer containing an XC or assembly program.
  """
  srcfile = name + '.' + ext
  outfile = name + '.o'
  vmsg(v, 'Assembling '+srcfile+' -> '+outfile)
  util.write_file(srcfile, string)
  if ext == 'xc':
    s = util.call([XCC, srcfile, '-o', outfile] + ASSEMBLE_FLAGS, v=show_calls)
    print(s, end='')
  elif ext == 'S':
    s = util.call([XAS, srcfile, '-o', outfile], v=show_calls)
    print(s, end='')
  if not save_temps: 
    os.remove(srcfile)

def assemble_runtime(device, show_calls, v):
  vmsg(v, 'Compiling runtime:')
  for x in RUNTIME_FILES:
    objfile = x+'.o'
    vmsg(v, '  '+x+' -> '+objfile)
    s = util.call([XCC, config.XS1_RUNTIME_PATH+'/'+x, 
      '-o', objfile] + ASSEMBLE_FLAGS, v=show_calls)
    print(s, end='')

def link_master(device, show_calls, v):
  """ 
  The jump table must be located at _cp and the common elements of the
  constant and data pools must be in the same positions relative to _cp and
  _dp in the master and slave images.
  """
  vmsg(v, 'Linking master -> '+MASTER_XE)
  s = util.call([XCC, target_1core(), 
    'system.S.o', 
    'system.xc.o',
    'control.xc.o',
    'worker.xc.o',
    'source.xc.o', 
    'host.xc.o', 
    'host.S.o',
    'connect.xc.o',
    'master.xc.o', 
    'master.S.o',
    'program.o',
    'memory.c.o', 
    'pointer.c.o', 
    'util.xc.o',
    MASTER_TABLES+'.o', 
    CONST_POOL+'.o',
    'globals.S.o',
    '-o', MASTER_XE] + LINK_FLAGS, 
    v=show_calls)
  print(s, end='')

def link_slave(device, show_calls, v):
  """
  As above.
  """
  vmsg(v, 'Linking slave -> '+SLAVE_XE)
  s = util.call([XCC, target_1core(), 
    'system.S.o', 
    'system.xc.o',
    'control.xc.o',
    'worker.xc.o',
    'source.xc.o', 
    'host.xc.o', 
    'host.S.o',
    'connect.xc.o',
    'slave.S.o',
    'memory.c.o', 
    'pointer.c.o', 
    'util.xc.o', 
    CONST_POOL+'.o',
    'globals.S.o',
    '-o', SLAVE_XE] + LINK_FLAGS,
    v=show_calls)
  print(s, end='')

def replace_images(show_calls, v):
  vmsg(v, 'Creating new executable')
  util.call([XCC, target_2core(), config.XS1_RUNTIME_PATH+'/container.xc', '-o', FINAL_XE])
  util.call([XOBJDUMP, '--split', MASTER_XE], v=show_calls)
  util.call([XOBJDUMP, FINAL_XE, '-r', '0,0,image_n0c0.elf'], v=show_calls)
  util.call([XOBJDUMP, '--split', SLAVE_XE], v=show_calls)
  util.call([XOBJDUMP, FINAL_XE, '-r', '0,1,image_n0c0.elf'], v=show_calls)

def append_header(device, outfile, show_calls, v):
  vmsg(v, 'Appending binary header')
  xe = open(FINAL_XE, "rb")
  se = open(outfile, "wb")
  try:
    se.write(bytes('SIRE', 'UTF-8'))
    se.write(struct.pack('I', device.num_cores()))
    se.write(xe.read())
  finally:
    xe.close()
    se.close()

def modify_assembly(sig, lines, v):
  """ 
  Perform modifications on assembly output.
  """
  vmsg(v, 'Modifying assembly output')
  
  #print(''.join(lines))
  (lines, cp) = extract_constants(lines, v)
  lines = insert_bottom_labels(sig, lines, v)
  #lines = insert_frame_sizes(sig, lines, v)
  lines = rewrite_calls(sig, lines, v)
  lines.insert(0, '###### MODIFIED ######\n')
  #print(''.join(lines))

  return (lines, cp)

def extract_constants(lines, v):
  """ 
  Extract constant sections only within the elimination block of a function.
  This covers all constants local to a function. This is to differentiate
  constants associated with and declared global.
   - Don't include elimination blocks for strings.
   - Make extracted labels global.
  NOTE: this assumes a constant section will be terminated with a .text,
  (which may not always be true?).
  """
  vmsg(v, '  Extracting constants')
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

def insert_bottom_labels(sig, lines, v):
  """
  Insert bottom labels for each function.
  """
  # Look for the structure and insert:
  # > .globl <bottom-label>
  #   foo:
  #   ...
  # > <bottom-label>
  #   .cc_bottom foo.function
  
  vmsg(v, '  Inserting function labels')
  
  # For each function, for each line...
  # (Create a new list and modify it each time...)
  b = False
  for x in sig.mobile_proc_names:
    new = []
    for (i, y) in enumerate(lines):
      new.append(y)
      if y == x+':\n' and not b:
        new.insert(len(new)-1, 
            '.globl '+function_label_bottom(x)+'\n')
        b = True
      elif y[0] == '.' and b:
        if y.split()[0] == '.cc_bottom':
          new.insert(len(new)-1, 
              function_label_bottom(x)+':\n')
          b = False
    lines = new

  return lines

def rewrite_calls(sig, lines, v):
  """ 
  Rewrite calls to program functions to branch through the jump table.
  """
  vmsg(v, '  Rewriting calls')
  for (i, x) in enumerate(lines):
    frags = x.strip().split()
    names = builtin.runtime_functions + sig.mobile_proc_names 
    if frags and frags[0] == 'bl' and frags[1] in names:
      lines[i] = '\tbla cp[{}+{}]\n'.format(defs.LABEL_JUMP_TABLE, 
          names.index(frags[1])*defs.BYTES_PER_WORD)
  return lines

def build_master_tab_init(sig, buf, v):
  assert (len(sig.mobile_proc_names) + defs.JUMP_INDEX_OFFSET) <= defs.JUMP_TABLE_SIZE
  vmsg(v, 'Building master table initialisation ({}/{})'.format(
    len(sig.mobile_proc_names), defs.JUMP_TABLE_SIZE))
  buf.write('#include "xs1/definitions.h"\n')

  # Data section
  buf.write('.section .dp.data, "awd", @progbits\n')
  buf.write('.align {}\n'.format(defs.BYTES_PER_WORD))
  
  buf.write('_numProgEntries:\n')
  buf.write('.globl _numProgEntries\n')
  buf.write('.set _numProgEntries.globound, {}\n'.format(defs.BYTES_PER_WORD))
  buf.write('\t.word {}\n'.format(len(sig.mobile_proc_names)))

  buf.write('_jumpLocations:\n')
  buf.write('.globl _jumpLocations\n')
  buf.write('.set _jumpLocations.globound, {}\n'.format(
      len(sig.mobile_proc_names)*defs.BYTES_PER_WORD))
  for x in sig.mobile_proc_names:
    buf.write('\t.word {}\n'.format(x))
  
  buf.write('.align {}\n'.format(defs.BYTES_PER_WORD))
  buf.write('.globl '+defs.LABEL_SIZE_TABLE+', "a(:ui)"\n')
  buf.write('.set {}.globound, {}\n'.format(
    defs.LABEL_SIZE_TABLE, defs.BYTES_PER_WORD*defs.SIZE_TABLE_SIZE))
  buf.write(defs.LABEL_SIZE_TABLE+':\n')
  # Pad runtime entries
  for x in range(defs.JUMP_INDEX_OFFSET):
    buf.write('\t.word 0\n')
  # Program procedure entries
  for x in sig.mobile_proc_names:
    buf.write('\t.word {}-{}+{}\n'.format(
      function_label_bottom(x), x, defs.BYTES_PER_WORD))
  # Pad any unused space
  remaining = defs.SIZE_TABLE_SIZE - (defs.JUMP_INDEX_OFFSET +
      len(sig.mobile_proc_names))
  buf.write('\t.space {}\n'.format(remaining*defs.BYTES_PER_WORD))

def dump_memory_use():
  TEXT  = 0
  DATA  = 1
  BSS   = 2
  TOTAL = 3

  def size(v):
    return '{:>6} {:>8}'.format(v, '({:,.2f}KB)'.format(v/1000))

  s = util.call([XOBJDUMP, '--size', MASTER_XE])
  m = re.findall(r' *([0-9]+) *([0-9]+) *([0-9]+) *([0-9]+)', s)
  master_sizes = [int(x) for x in m[0]]
  assert len(m) == 1
  s = util.call([XOBJDUMP, '--size', SLAVE_XE])
  m = re.findall(r' *([0-9]+) *([0-9]+) *([0-9]+) *([0-9]+)', s)
  slave_sizes = [int(x) for x in m[0]]
  assert len(m) == 1
  print('Total memory:           '+size(defs.RAM_SIZE))
  print()
  
  print('Kernel stack space:     '+size(defs.KERNEL_SPACE))
  print('Thread stack space:     '+size(defs.THREAD_STACK_SPACE))
  print('Number of threads:      {:>6}'.format(defs.MAX_THREADS))
  thread_stack_use = defs.MAX_THREADS*defs.THREAD_STACK_SPACE
  total_stack_use = thread_stack_use+defs.KERNEL_SPACE
  print('Total thread stack use: '+size(thread_stack_use))
  print('Total stack use:        '+size(total_stack_use))
  print()

  runtime_size = slave_sizes[TEXT]+slave_sizes[DATA]
  program_size = master_sizes[TEXT]+master_sizes[DATA]-runtime_size
  print('Runtime size:           '+size(runtime_size))
  print('Program size:           '+size(program_size))
  print()

  print('Master memory use: ')
  print('  text:                 '+size(master_sizes[TEXT]))
  print('  data:                 '+size(master_sizes[DATA]))
  print('  bss:                  '+size(master_sizes[BSS]))
  print('  stack:                '+size(total_stack_use))
  print('  '+('-'*39))
  master_total = master_sizes[TOTAL]+total_stack_use
  master_remaining = defs.RAM_SIZE - master_total
  print('  Total:                '+size(master_total))
  print('  Remaining:            '+size(master_remaining))
  print()
  
  print('Slave memory use: ')
  print('  text:                 '+size(slave_sizes[TEXT]))
  print('  data:                 '+size(slave_sizes[DATA]))
  print('  bss:                  '+size(slave_sizes[BSS]))
  print('  stack:                '+size(total_stack_use))
  print('  '+('-'*39))
  slave_total = slave_sizes[TOTAL]+total_stack_use
  slave_remaining = defs.RAM_SIZE - slave_total
  print('  Total:                '+size(slave_total))
  print('  Remaining:            '+size(slave_remaining))

def cleanup(v):
  """ 
  Renanme the output file and delete any temporary files.
  """
  vmsg(v, 'Cleaning up')
  
  # Remove specific files
  util.remove_file(MASTER_XE)
  util.remove_file(SLAVE_XE)
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

def target_1core():
  return config.INSTALL_PATH+'/device/xs1/XS1-L1A.xn'

def target_2core():
  return config.INSTALL_PATH+'/device/xs1/XS1-L2A.xn'

def function_label_top(name):
  return '.'+name+'.top'

def function_label_bottom(name):
  return '.'+name+'.bottom'

#def function_label_framesize( name):
#  return '.'+name+'.framesize'

