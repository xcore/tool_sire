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
  t.out('GETR_SYNC_THREAD(_sync, _threads[_i]);')

  # Set lr = slave_exit_label
  t.asm('ldap r11, '+sync_label+' ; init t[%0]:lr, r11',
      inops=['_threads[_i]'], clobber=['r11'])

  t.blocker.end()

def is_ref(t):
  return (t == T_REF_SINGLE
      or t == T_CHANEND_SINGLE
      or t == T_CHANEND_SERVER_SINGLE
      or t == T_CHANEND_CLIENT_SINGLE)

#def num_ref_singles(params):
#  """
#  Return the number of referenced single variables in a param list.
#  """
#  return reduce(lambda x,y: x+(1 if is_ref(y.symbol.type) else 0), params, 0)

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
  #n_ref_singles = num_ref_singles(params)
  #n_stack_args = num_stack_args(pcall)
  #ext = n_stack_args
  
  #t.out('THREAD_SP(TID_MASK(_threads[{0}]), _sps[{0}]);'.format(index))
  t.out('_tsp = _sp() - (TID_MASK(_threads[{0}])*THREAD_STACK_SPACE);'
      .format(index))
  
  # Load sp address and extend it if we need space for refd vars
  #if ext > 0:
  #  t.out('_sps[{}] -= {};'.format(index, '' if ext == 0 else 
  #      '{}*{}'.format(ext, defs.BYTES_PER_WORD)))
  #  t.asm('init t[%0]:sp, %1', inops=[tid, '_sps[{}]'.format(index)])

  # Write the value of referenced variables to the stack
  #ref_addr_exprs = []
  #j = 0
  #for (i, (x, y)) in enumerate(zip(pcall.args, params)):
  #  a = None
  #  if is_ref(y.symbol.type):
  #    assert isinstance(x, ast.ExprSingle)
  #    stw(t, t.expr(x), '_sps[{}]'.format(index), 1+n_stack_args+j)
  #    a = '_sps[{}]+({}*{})'.format(index, 1+n_stack_args+j, defs.BYTES_PER_WORD)
  #    j = j + 1
  #  ref_addr_exprs.append(a)

  # Write arguments to registers and stack
  for (i, (x, y)) in enumerate(zip(pcall.args, params)):

    # For references, we pass the address, via a pointer function hack
    if y.symbol.type == T_REF_SINGLE:
      value = '_pointerInt({})'.format(t.expr(x))
    elif y.symbol.type == T_CHANEND_SINGLE or \
      y.symbol.type == T_CHANEND_SERVER_SINGLE or \
      y.symbol.type == T_CHANEND_CLIENT_SINGLE:
      value = '_pointerUnsigned({})'.format(t.expr(x))
    # Otherwise we set this directly
    else:
      value = t.expr(x)
    
    if i < defs.NUM_PARAM_REGS:
      t.asm('set t[%0]:r{}, %1'.format(i), inops=[tid, value])
    else:
      stw(t, value, '_tsp', i-defs.NUM_PARAM_REGS+1)

def master_unset(t, index, pcall):
  """
  Grab all updates to referenced single variables from each slave thread.
  """
  assert isinstance(pcall, ast.StmtPcall)
  t.comment('Master unset slave {}'.format(index))
  params = t.sig.get_params(pcall.name)
  #n_stack_args = num_stack_args(pcall)

  # Load referenced variable values back
  #j = 0
  #for (i, (x, y)) in enumerate(zip(pcall.args, params)):
  #  if is_ref(y.symbol.type):
  #    ldw(t, t.expr(x), '_sps[{}]'.format(index), 1+n_stack_args+j)
  #    # This seems to solve a register problem...
  #    t.out('{0} = {0}-1;'.format(t.expr(x)))
  #    t.out('{0} = {0}+1;'.format(t.expr(x)))
  #    j = j + 1
 
def slave_unset(t):
  """
  This (is not ideal but) ensures any extended stack pointers are restored.
  TODO: Fix the << 8 
  """
  #t.blocker.begin()
  #t.out('unsigned _sp;')
  #t.out('unsigned _tid;')
  #t.out('THREAD_ID(_tid);')
  #t.out('THREAD_SP(_tid, _sp);')
  #t.asm('set sp, %0', inops=['_sp'])
  #t.blocker.end()

def gen_par(t, node, chans):
  """
  Generate a parallel block.
  """
  num_slaves = len(node.stmt) - 1
  sync_label = t.get_label()
  exit_label = t.get_label()
  slave_exit_labels = [t.get_label() for x in range(num_slaves)]

  # Declare sync variable and array to store thread identifiers
  t.out('unsigned _sync;')
  #t.out('unsigned _spbase;')
  t.out('unsigned _threads[{}];'.format(num_slaves))
  t.out('unsigned _tsp;'.format(num_slaves))
  t.out('unsigned _dp;')
  t.out('unsigned _cp;')

  # Get a thread synchroniser
  t.comment('Get a sync, sp base, _spLock and claim num threads')
  t.out('GETR_SYNC(_sync);')
   
  # Slave initialisation
  init_slaves(t, sync_label, num_slaves)
   
  # Individual slave setup
  [thread_set(t, i, x, slave_exit_labels) for (i, x) in enumerate(node.stmt[1:])]

  # Master synchronise and run
  t.comment('Master fork')
  t.asm('msync res[%0]', inops=['_sync']) # Fork
  t.stmt(node.stmt[0], chans)
 
  # Master join
  t.comment('Master join')
  t.asm('mjoin res[%0]', inops=['_sync'])

  # Master exit
  t.asm('bu '+exit_label)

  # Slave synchronise and exit
  t.comment('Slave exit')
  t.asm(sync_label+':')
  #slave_unset(t)
  t.asm('ssync') # Stop

  # Ouput exit label 
  t.comment('Exit, free _sync, restore _sp and _numthreads')
  t.asm(exit_label+':')
 
  # NOTE: when freer _sync appears after the loads back from the stack, there
  # was a situation where the compiler was saving the correct value from the
  # destination of a load before the load was executed with optimisation levels
  # > 1. Not sure if this is a bug with the compiler or the threading
  # implementation.

  # Free synchroniser resource
  t.out('FREER(_sync);')

  # Individual slave teardown
  [master_unset(t, i, x) for (i, x) in enumerate(node.stmt[1:])]
  
