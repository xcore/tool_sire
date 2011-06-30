# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
import definitions as defs
from typedefs import *

def calc_closure_size(num_procs, params):
  """
  Calculate the size of a process closure
  """
  closure_size = 2 + num_procs;
  for (i, x) in enumerate(params):

    if x.symbol.type == T_REF_ARRAY:
      closure_size = closure_size + 3

    elif x.symbol.type == T_REF_SINGLE:
      closure_size = closure_size + 2

    elif x.symbol.type == T_VAL_SINGLE: 
      closure_size = closure_size + 2

    elif x.symbol.type == T_CHANEND_SINGLE:
      closure_size = closure_size + 2

    else:
      assert 0

  return closure_size

def argument(t, n, celem, proc_name, args, index, arg, param):
  """
  Generate a closure entry for an argument
    Array: (0, length, address)
    Var:   (1, address)
    Val:   (2, value)
  """
  # If the parameter type is an array reference
  if param.symbol.type == T_REF_ARRAY:

    # Output the length of the array. Either it's a variable in the list
    # of the parameters or it's a constant value.
    t.comment('Array')
    n = celem(n, 't_arg_ALIAS')
    if param.symbol.value == None:
      q = t.sig.lookup_array_qualifier(proc_name, index)
      n = celem(n, t.expr(args[q]))
    else:
      n = celem(n, t.expr(param.expr))
     
    # If the elem is a proper array, load the address
    if arg.elem.symbol.type == T_VAR_ARRAY:
      tmp = t.blocker.get_tmp()
      t.asm('mov %0, %1', outop=tmp, inops=[arg.elem.name])
      n = celem(n, tmp)
    # Otherwise, just assign
    if arg.elem.symbol.type == T_REF_ARRAY:
      n = celem(n, t.expr(arg))
  
  # Variable reference
  elif param.symbol.type == T_REF_SINGLE:
    t.comment('Variable reference')
    n = celem(n, 't_arg_VAR')
    tmp = t.blocker.get_tmp()
    t.asm('mov %0, %1', outop=tmp,
        inops=['('+arg.elem.name+', unsigned[])'])
    n = celem(n, tmp)

  # Value
  elif param.symbol.type == T_VAL_SINGLE:
    t.comment('Value')
    n = celem(n, 't_arg_VAL')
    n = celem(n, t.expr(arg))

  # Channel end
  elif param.symbol.type == T_CHANEND_SINGLE:
    t.comment('Channel end')
    n = celem(n, 't_arg_CHANEND')
    n = celem(n, t.expr(arg))

  else:
    assert 0

  return n

def gen_on(t, node):
    """
    Generate an on statement, given the translation object t and the AST node.
    We expect the form::

      on <expr> do <stmt>
    """
    assert isinstance(node.stmt, ast.StmtPcall)
    pcall = node.stmt
    proc_name = node.stmt.name
    num_args = len(pcall.args) 
    num_procs = len(t.child.children[proc_name]) + 1
    params = t.sig.get_params(pcall.name)

    # Calculate closure size 
    closure_size = calc_closure_size(num_procs, params)

    # If the destination is the current processor, then we just evaluate the
    # statement locally.
    t.comment('On')
    t.out('if ({} == _procid())'.format(t.expr(node.expr)))

    # Local evaluation
    t.blocker.begin()
    t.stmt(node.stmt)
    t.blocker.end()

    t.out('else')

    # Remote evaluation
    t.blocker.begin()
    t.out('unsigned _closure[{}];'.format(closure_size))
    n = 0

    # Output an element of the closure
    def celem(n, e):
      t.out('_closure[{}] = {};'.format(n, e))
      return n + 1

    # Header: (#args, #procs)
    t.comment('Header: (#args, #procs)')
    n = celem(n, num_args)
    n = celem(n, num_procs)

    # Arguments: 
    for (i, (x, y)) in enumerate(zip(pcall.args, params)):
      n = argument(t, n, celem, proc_name, pcall.args, i, x, y)

    # Procedures: (jumpindex)*
    t.comment('Proc: parent '+proc_name)
    n = celem(n, defs.JUMP_INDEX_OFFSET
        +t.sig.mobile_proc_names.index(proc_name))
    for x in t.child.children[proc_name]:
      t.comment('Proc: child '+x)
      n = celem(n, defs.JUMP_INDEX_OFFSET
          +t.sig.mobile_proc_names.index(x))

    # Call runtime TODO: length argument?
    t.out('{}({}, _closure);'.format(defs.LABEL_CREATE_PROCESS, 
      t.expr(node.expr)))

    t.blocker.end()

