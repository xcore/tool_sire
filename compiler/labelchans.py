# Copyright (c) 2011, James Hanlon, All rights reserved
## This software is freely distributable under a derivative of the
## University of Illinois/NCSA Open Source License posted in
## LICENSE.txt and at <http://github.xcore.com/>

import sys
import copy
import collections
from itertools import product

import ast
from walker import NodeWalker
from typedefs import *
from subelem import SubElem
from evalexpr import EvalExpr

from printer import Printer

class ChanUse(object):
  def __init__(self, name, index):
    self.index = index
    self.offsets = []

  def add_offset(self, offset):
    master = len(self.offsets) == 0
    self.offsets.append(offset)
    return master


class ChanTable(object):
  """
  A table to record the location of channel ends and their names.
  """
  def __init__(self, name):
    self.name = name
    self.tab = {}
    
  def key(self, name, index):
    """
    Given a channel name and its index return a key concatenating these.
    """
    return '{}{}'.format(name, '' if index==None else index)

  def insert(self, name, index, offset):
    """
    Add the offsets to the label table. A master channel is allocated on the
    basis of which side appears first in the traversal of AST.
    """
    # Create the entry if it doesn't exist
    if not name in self.tab:
      self.tab[name] = []
    
    # Try and find an existing offset
    item = None
    for x in self.tab[name]:
      if x.index == index:
        item = x

    # Add it as a master if it doesn't exist
    if not item:
      item = ChanUse(name, index)
      self.tab[name].append(item)
   
    # Set the master or slave offset
    return item.add_offset(offset)

  def display(self):
    print('Channel table for procedure '+self.name+':')
    for x in self.tab.keys():
      print('  {}: \n{}'.format(x, '\n'.join(
        ['    ({}: {})'.format(y.index, 
          ', '.join(['{}'.format(z) for z in y.offsets])) 
          for y in self.tab[x]])))


class LabelChans(NodeWalker):
  """
  For each procedure definition, construct a table which records for each use
  of a channel the offsets of the master and slave processes (relative to the
  base). For replicators, expand array subscripts over the range of the
  iterators and tag each with its offset relative to the declaration of the
  channel. Then label each channel with the relative offset from the master to
  the slave.
  """
  def __init__(self, print_debug=False):
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def single_channel(self, tab, stmt, name):
    """
    Process a single (non-subscripted) channel use by evaluating its offset
    and then adding it to the channel table and returning its use tuple. The
    offset will not contain any variables.
    """
    offset_value = EvalExpr().expr(stmt.offset)
    master = tab.insert(name, None, offset_value)
    self.debug('  {} at {}'.format(name, offset_value))
    return (name, None, master)

  def subscript_channel(self, iters, tab, stmt, name, expr):
    """
    Expand the use of a channel subscript over a set of iterators and determine
    for each the value of its index and offset, and then add this to the
    channel table and set of uses.
    """
    #print(Printer().expr(elem.expr))
    #print(Printer().expr(stmt.offset))
    uses = []

    # Iterate over cartesian product of iterator ranges
    ranges = [range(x.base_value, x.base_value+x.count_value) for x in iters]
    for x in product(*ranges):

      # Deep copy expressions so we can modify them
      index_expr = copy.deepcopy(expr)
      offset_expr = copy.deepcopy(stmt.offset)

      # Substitute index variables for values
      for (y, z) in zip(iters, x):
        index_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
        offset_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))

      # Evaluate the expressions
      index_value = EvalExpr().expr(index_expr)
      offset_value = EvalExpr().expr(offset_expr)

      # Add to the table
      master = tab.insert(name, index_value, offset_value)

      # Add the expanded channel use (name, index) to a list
      uses.append((name, index_value, master))

      self.debug('  {}[{}] at {}'.format(name, index_value, offset_value))
    
    return uses

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================

  def defn(self, node):
    self.debug('New channel scope: '+node.name)
    node.chantab = ChanTable(node.name)
    node.uses = self.stmt(node.stmt, [], node.chantab)
    node.chantab.display()
  
  # Statements ==========================================

  # Top-level statements where connections are inserted as we distribute on
  # these boundaries. The set use_instances contains all the unique occurances
  # of channels in the contained process.

  def stmt_rep(self, node, iters, tab):
    iters = iters + node.indicies
    use_instances = self.stmt(node.stmt, iters, tab)
    
    node.uses = []
    for x in use_instances:
      if x[1] == None:
        node.uses.append(self.single_channel(tab, node.stmt, x[0]))
      else:
        node.uses.extend(self.subscript_channel(
          iters, tab, node.stmt, x[0], x[1]))

    return set()
  
  def stmt_par(self, node, iters, tab):
    
    node.uses = []
    for x in node.stmt:
      use_instances = self.stmt(x, iters, tab)
    
      stmt_uses = []
      for x in use_instances:
        if x[1] == None:
          stmt_uses.append(self.single_channel(tab, node, x[0]))
        else:
          stmt_uses.extend(self.subscript_channel(
            iters, tab, node, x[0], x[1]))
      node.uses.append(stmt_uses)
    
    return set()
 
  # Statements containing uses of channels.

  def stmt_in(self, node, iters, tab):
    self.debug('out channel {}:'.format(node.left.name))
    
    if isinstance(node.left, ast.ElemId):
      return set([(node.left.name, None)])
    
    elif isinstance(node.left, ast.ElemSub):
      return set([(node.left.name, node.left.expr)])
    
    else:
      assert 0

  def stmt_out(self, node, iters, tab):
    self.debug('in channel {}:'.format(node.left.name))

    if isinstance(node.left, ast.ElemId):
      return set([(node.left.name, None)])
    
    elif isinstance(node.left, ast.ElemSub):
      return set([(node.left.name, node.left.expr)])
    
    else:
      assert 0

  def stmt_pcall(self, node, iters, tab):
    uses = set()
    for x in node.args:
      if isinstance(x, ast.ExprSingle):

        if (isinstance(x.elem, ast.ElemId)
            and x.elem.symbol.type == T_CHAN_SINGLE):
          self.debug('single arg channel {}:'.format(x.elem.name))
          uses |= set([(x.elem.name, None)])

        elif (isinstance(x.elem, ast.ElemSub)
            and x.elem.symbol.type == T_CHAN_ARRAY):
          self.debug('subscript arg channel {}:'.format(x.elem.name))
          uses |= set([(x.elem.name, x.elem.expr)])

        else:
          pass

    return uses
    
  # Other statements containing processes

  def stmt_seq(self, node, iters, tab):
    uses = set()
    [uses.update(self.stmt(x, iters, tab)) for x in node.stmt]
    return uses

  def stmt_if(self, node, iters, tab):
    uses = self.stmt(node.thenstmt, iters, tab)
    uses |= self.stmt(node.elsestmt, iters, tab)
    return uses

  def stmt_while(self, node, iters, tab):
    return self.stmt(node.stmt, iters, tab)

  def stmt_for(self, node, iters, tab):
    return self.stmt(node.stmt, iters, tab)

  # Statements not containing processes or channels uses

  def stmt_ass(self, node, iters, tab):
    return set()

  def stmt_alias(self, node, iters, tab):
    return set()

  def stmt_skip(self, node, iters, tab):
    return set()

  def stmt_return(self, node, iters, tab):
    return set()

  # Prohibited statements

  def stmt_on(self, node, iters, tab):
    assert 0

  def stmt_connect(self, node, iters, tab):
    assert 0

