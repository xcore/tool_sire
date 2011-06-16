# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

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
    
    # Calculate closure size 
    closure_size = 2 + num_procs;
    for (i, x) in enumerate(pcall.args):
      t = t.sig.lookup_param_type(proc_name, i)
      if t.form == 'array': closure_size = closure_size + 3
      elif t.form == 'single': closure_size = closure_size + 2 

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
    def celem(i, e):
      t.out('_closure[{}] = {};'.format(i, e))
      return n + 1

    # Header: (#args, #procs)
    t.comment('Header: (#args, #procs)')
    n = celem(n, num_args)
    n = celem(n, num_procs)

    # Arguments: 
    #   Array: (0, length, address)
    #   Var:   (1, address)
    #   Val:   (2, value)
    if pcall.args:
      for (i, (x, y)) in enumerate(
          zip(pcall.args, t.sig.get_params(pcall.name))):
        t = t.sig.lookup_param_type(proc_name, i)

        # If the parameter type is an array reference
        if t == T_REF_ARRAY:

          # Output the length of the array. Either it's a variable in the list
          # of the parameters or it's a constant value.
          n = celem(n, 't_arg_ALIAS')
          if y.symbol.value == None:
            q = t.sig.lookup_array_qualifier(proc_name, i)
            n = celem(n, t.expr(pcall.args[q]))
          else:
            n = celem(n, t.expr(y.expr))
           
          # If the elem is a proper array, load the address
          if x.elem.symbol.type == T_VAR_ARRAY:
            t.comment('Array')
            tmp = t.blocker.get_tmp()
            t.asm('mov %0, %1', outop=tmp, inops=[x.elem.name])
            n = celem(n, tmp)
          # Otherwise, just assign
          if x.elem.symbol.type == T_REF_ARRAY:
            t.comment('Array reference')
            n = celem(n, t.expr(x))
        
        # Otherwise, a single
        elif t.form == 'single':

          # Variable reference
          if t.specifier == 'ref':
            t.comment('Variable reference')
            n = celem(n, 't_arg_VAR')
            tmp = t.blocker.get_tmp()
            t.asm('mov %0, %1', outop=tmp,
                inops=['('+x.elem.name+', unsigned[])'])
            n = celem(n, tmp)

          # Value
          elif t.specifier == 'val':
            t.comment('Value')
            n = celem(n, 't_arg_VAL')
            n = celem(n, t.expr(x))

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

