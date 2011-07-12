# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from functools import reduce
import definitions as defs
from typedefs import *
import ast

def init_slaves(t, sync_label, num_slaves):
  """ 
  Generate the initialisation for a slave thread, in the body of a for
  loop with _i indexing the thread number.
   - Get a synchronised thread
   - Set the sp, lr, dp, cp
  """
  # Loop over each of the slave threads
  t.comment('Initialise slave threads')
  t.out('for(int _i=0; _i<{}; _i++)'.format(num_slaves))
  t.blocker.begin()
  
  # Get a synchronised thread
  t.out('unsigned _t;')
  t.asm('getst %0, res[%1]', outop='_t', inops=['_sync'])

  # Set lr = slave_exit_label
  t.asm('ldap r11, '+sync_label+' ; init t[%0]:lr, r11',
      inops=['_t'], clobber=['r11'])

  # Setup dp, cp
  t.asm('init t[%0]:dp, %1', inops=['_t', '_dp'])
  t.asm('init t[%0]:cp, %1', inops=['_t', '_cp'])

  # Copy thread id to the array
  t.out('_threads[_i] = _t;')
  t.blocker.end()
  
def num_ref_singles(params):
  """
  Return the number of referenced single variables in a param list.
  """
  return reduce(lambda x,y: x+(1 if y.symbol.type==T_REF_SINGLE else 0), 
      params, 0)

def num_stack_args(pcall):
  """
  Return the number of arguments to be passed on the stack for a call.
  """
  return (len(pcall.args)-defs.NUM_PARAM_REGS if
      len(pcall.args)>defs.NUM_PARAM_REGS else 0)

def stw(t, source, base, index):
  """
  Output a store immediate if the index is < 11.
  """
  if index <= 11:
    t.asm('stw %0, %1[{}]'.format(index), inops=[source, base])
  else:
    t.asm('stw %0, %1[%2]', 
        inops=[source, base, '{}'.format(index)])
      
def ldw(t, dest, base, index):
  """
  Output a load immediate if the index is < 11.
  """
  if index <= 11:
    t.asm('ldw %0, %1[{}]'.format(index), outop=dest, inops=[base])
  else:
    t.asm('ldw %0, %1[%2]'.format(),
          outop=dest, inops=[base, '{}'.format(index)])

def thread_set(t, index, pcall, slave_exit_labels):
  """
  Individually initialise a threads pc and parameter values.
  """
  assert isinstance(pcall, ast.StmtPcall)
  t.comment('Master set slave {}'.format(index))
  tid = '_threads[{}]'.format(index)
  params = t.sig.get_params(pcall.name)

  # Set pc = &pcall (from jump table)
  t.asm('ldw r11, cp[{}] ; init t[%0]:pc, r11'
      .format(defs.JUMP_INDEX_OFFSET +
        t.sig.mobile_proc_names.index(pcall.name)), 
        inops=[tid], clobber=['r11'])

  # Count the number of referenced single variable parameters
  # Calculate the extra stack space for arguments
  n_ref_singles = num_ref_singles(params)
  n_stack_args = num_stack_args(pcall)
  ext = n_ref_singles + n_stack_args
  
  # Move sp away: sp -= THREAD_STACK_SPACE and save it
  t.out('_sps[{}] = _sp - ((({}>>8)&0xFF) * THREAD_STACK_SPACE){};'
      .format(index, tid, '' if ext == 0 else 
        ' - ({}*{})'.format(ext, defs.BYTES_PER_WORD)))
  t.asm('init t[%0]:sp, %1', inops=[tid, '_sps[{}]'.format(index)])

  # Write the value of referenced variables to the stack
  ref_addr_exprs = []
  j = 0
  for (i, (x, y)) in enumerate(zip(pcall.args, params)):
    a = None
    if y.symbol.type == T_REF_SINGLE:
      assert isinstance(x, ast.ExprSingle)
      stw(t, t.expr(x), '_sps[{}]'.format(index), 1+n_stack_args+j)
      a = '_sps[{}]+({}*{})'.format(index, 1+n_stack_args+j, defs.BYTES_PER_WORD)
      j = j + 1
    ref_addr_exprs.append(a)

  # Write arguments to registers and stack
  for (i, (x, y)) in enumerate(zip(pcall.args, params)):

    # For references, we pass the address
    if y.symbol.type == T_REF_SINGLE:
      value = ref_addr_exprs[i]
    # Otherwise we set this directly
    else:
      value = t.expr(x)
    
    if i < defs.NUM_PARAM_REGS:
      t.asm('set t[%0]:r{}, %1'.format(i), inops=[tid, value])
    else:
      stw(t, value, '_sps[{}]'.format(index), i-defs.NUM_PARAM_REGS+1)

def thread_unset(t, index, pcall):
  """
  Grab all updates to referenced single variables from each slave thread.
  """
  assert isinstance(pcall, ast.StmtPcall)
  t.comment('Master unset slave {}'.format(index))
  params = t.sig.get_params(pcall.name)
  n_stack_args = num_stack_args(pcall)
  j = 0
  for (i, (x, y)) in enumerate(zip(pcall.args, params)):
    if y.symbol.type == T_REF_SINGLE:
      ldw(t, t.expr(x), '_sps[{}]'.format(index), 1+n_stack_args+j)
      j = j + 1

def gen_par(t, node):
  """
  Generate a parallel block.
  """
  num_slaves = len(node.stmt) - 1
  sync_label = t.get_label()
  exit_label = t.get_label()
  slave_exit_labels = [t.get_label() for x in range(num_slaves)]
  t.blocker.begin()

  # Declare sync variable and array to store thread identifiers
  t.out('unsigned _sync;')
  t.out('unsigned _spbase;')
  t.out('unsigned _threads[{}];'.format(num_slaves))
  t.out('unsigned _sps[{}];'.format(num_slaves))
  t.out('unsigned _dp;')
  t.out('unsigned _cp;')

  # Get a thread synchroniser
  t.comment('Get a sync, sp base, _spLock and claim num threads')
  t.asm('getr %0, " S(XS1_RES_TYPE_SYNC) "', outop='_sync');
   
  # Load the address of sp
  t.asm('ldaw %0, sp[0x0]', outop='_spbase')
  t.asm('ldaw %0, dp[0x0]', outop='_dp', clobber=['r11'])
  t.asm('ldaw r11, cp[0x0] ; mov %0, r11',
      outop='_cp', clobber=['r11'])

  # Claim thread count
  t.asm('in r11, res[%0]', inops=['_numthreads_lock'], clobber=['r11'])
  t.out('_numthreads = _numthreads - {};'.format(num_slaves))
  t.asm('out res[%0], r11', inops=['_numthreads_lock'], clobber=['r11'])

  # Slave initialisation
  init_slaves(t, sync_label, num_slaves)
   
  # Individual slave setup
  [thread_set(t, i, x, slave_exit_labels) for (i, x) in enumerate(node.stmt[1:])]

  # Master synchronise and run
  t.comment('Master fork')
  t.asm('msync res[%0]', inops=['_sync'])
  t.stmt(node.stmt[0])
  t.asm('msync res[%0]', inops=['_sync'])
  
  # Individual slave teardown
  [thread_unset(t, i, x) for (i, x) in enumerate(node.stmt[1:])]
  
  t.comment('Master join')
  t.asm('mjoin res[%0]', inops=['_sync'])

  # Master exit
  t.asm('bu '+exit_label)

  # Slave synchronise and exit
  t.comment('Slave exit')
  t.asm(sync_label+':')
  t.asm('ssync')
  t.asm('ssync')

  # Ouput exit label 
  t.comment('Exit, free _sync, restore _sp and _numthreads')
  t.asm(exit_label+':')
  
  # Free synchroniser resource
  t.asm('freer res[%0]', inops=['_sync'])

  # Release thread count
  t.asm('in r11, res[%0]', inops=['_numthreads_lock'], clobber=['r11'])
  t.out('_numthreads = _numthreads + {};'.format(num_slaves))
  t.asm('out res[%0], r11', inops=['_numthreads_lock'], clobber=['r11'])

  t.blocker.end()

