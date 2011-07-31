# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ast
from walker import NodeWalker
from display import Display

class BuildCFG(NodeWalker):
  """
  A NodeWalker to build the Control-Flow Graph for the AST. 
   - For statements: set predecessor and successor lists and populate the use,
     def, in and out sets for liveness analysis.
   - For expressions return a set of used variable elements.

  Each statement returns a list of statements which exit it. For non-compound
  statements this is just the statement itself, for compound statements such as
  if, this is the 'then' and 'else' statements. These lists are then given as
  the predecessors to the next statement.
  """
  def __init__(self):
    pass

  def init_sets(self, node, pred, succ):
    node.pred = pred
    node.succ = succ
    node.use = set()
    node.defs = set()
    node.inp = set()
    node.out = set()

  def print_successors(self, stmt):
    print('{}:'.format(stmt))
    for y in stmt.succ:
      print('  {}'.format(y))
    print('')
   
  def run(self, node):
    """
    Walk each procedure definition.
    """
    [self.defn(x) for x in node.defs]
    
  def defn(self, node):
    """
    Before traversing the body statement we add arrays to an implicit uses
    set. Arrays are used implicitly by every statement as their live range
    is the entire procedure.
    """
    if node.stmt:
      node.pred = self.stmt(node.stmt, [], [])

    # Display the successors of each node
    #node.accept(Display(self.print_successors))

  # Statements ==========================================

  # Statements containing statements

  def stmt_seq(self, node, pred, succ):
    self.init_sets(node, pred, [node.stmt[0]])
    p = [node]
    for (i, x) in enumerate(node.stmt):
      s = [node.stmt[i+1]] if i<(len(node.stmt)-1) else succ
      p = self.stmt(x, p, s)
      #p = [node.stmt[i-1]] if i>0 else pred
      #s = [node.stmt[i+1]] if i<len(node.stmt)-1 else succ
    return p

  def stmt_par(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    p = []
    [p.extend(self.stmt(x, pred, succ)) for x in node.stmt]
    return p

  def stmt_rep(self, node, pred, succ):
    self.init_sets(node, pred, [node.stmt])
    node.defs |= set([x for x in node.indicies])
    [node.use.update(self.expr(x.base)) for x in node.indicies]
    [node.use.update(self.expr(x.count)) for x in node.indicies]
    return self.stmt(node.stmt, [node], succ)

  def stmt_on(self, node, pred, succ):
    self.init_sets(node, pred, [node.stmt])
    node.use |= self.expr(node.expr)
    return self.stmt(node.stmt, [node], succ)

  def stmt_if(self, node, pred, succ):
    self.init_sets(node, pred, [node.thenstmt, node.elsestmt])
    node.use |= self.expr(node.cond)
    p = self.stmt(node.thenstmt, [node], succ)
    p += self.stmt(node.elsestmt, [node], succ)
    return p

  def stmt_while(self, node, pred, succ):
    self.init_sets(node, pred, [node.stmt])
    node.use |= self.expr(node.cond)
    p = self.stmt(node.stmt, [node], [node]+succ)
    return [node] + p

  def stmt_for(self, node, pred, succ):
    self.init_sets(node, pred, [node.stmt])
    node.defs |= set([node.index])
    node.use |= self.expr(node.index.base)
    node.use |= self.expr(node.index.count)
    p = self.stmt(node.stmt, [node], [node]+succ)
    return [node] + p

  # Statements not containing statements

  def stmt_pcall(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    [node.use.update(self.expr(x)) for x in node.args]
    return [node]

  def stmt_ass(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.use |= self.expr(node.expr)
    node.defs |= set([node.left])

    # Writes to arrays, include them as a use so they are live until this
    # point.
    if isinstance(node.left, ast.ElemSub):
      node.use |= node.defs
    return [node]

  def stmt_in(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.defs |= self.expr(node.expr)
    node.use |= set([node.left])
    return [node]

  def stmt_out(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.use |= self.expr(node.expr)
    node.use |= set([node.left])

    # Writes to arrays, include them as a use so they are live until this
    # point.
    if isinstance(node.left, ast.ElemSub):
      node.use |= node.defs
    return [node]

  def stmt_alias(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.use |= self.elem(node.slice)
    node.defs |= set([node.left])

    # Add alias targets to use set to they are live until this point.
    node.use |= node.defs 
    return [node]

  def stmt_connect(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    if not node.expr == None: 
      node.use |= self.expr(node.expr)
    node.defs |= set([node.left])
    return [node]

  def stmt_skip(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    return [node]

  def stmt_assert(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.use |= self.expr(node.expr)
    return [node]
  
  def stmt_return(self, node, pred, succ):
    self.init_sets(node, pred, succ)
    node.use |= self.expr(node.expr)
    return [node]
  
  # Expressions =========================================

  def expr_single(self, node):
    return self.elem(node.elem)

  def expr_unary(self, node):
    return self.elem(node.elem)

  def expr_binop(self, node):
    c = self.elem(node.elem)
    c |= self.expr(node.right)
    return c
  
  # Elements= ===========================================

  # Identifier
  def elem_id(self, node):
    """
    We only want to return variables in the program/procedure scopes, not in
    the system scope.
    """
    #print('elem: '+node.name+', {}'.format(node.symbol.scope))
    return set([node]) if not node.symbol.scope == 'system' else set()

  # Array subscript
  def elem_sub(self, node):
    c = self.expr(node.expr)
    return c | set([node])

  # Array slice
  def elem_slice(self, node):
    c = self.expr(node.base)
    c |= self.expr(node.count)
    return c | set([node])

  # Index range
  def elem_index_range(self, node):
    node.defs |= set([node.name])
    node.use |= self.expr(node.base)
    node.use |= self.expr(node.count)

  def elem_group(self, node):
    return self.expr(node.expr)

  def elem_fcall(self, node):
    c = set()
    [c.update(self.expr(x)) for x in node.args]
    return c

  def elem_number(self, node):
    return set()

  def elem_boolean(self, node):
    return set()

  def elem_string(self, node):
    return set()

  def elem_char(self, node):
    return set()

