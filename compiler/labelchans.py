# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import copy
import collections
from itertools import product

import ast
from util import debug
from walker import NodeWalker
from typedefs import *
from chantab import ChanTable
from subelem import SubElem
from evalexpr import EvalExpr
from cmpexpr import CmpExpr
from indicies import *

from printer import Printer

DISPLAY_CHANTAB = False 

class LabelChans(NodeWalker):
  """
  For each procedure definition, construct a table which records for each use
  of a channel the locations of the master and slave processes (relative to the
  base). For replicators, expand array subscripts over the range of the
  iterators and tag each with its location. Then label each channel with the 
  relative offset from the master to the slave.
  """
  def __init__(self, device, errorlog, debug=False):
    self.device = device
    self.errorlog = errorlog
    self.debug = debug

  def single_channel(self, tab, stmt, name, chanend, chan_set):
    """
    Process a single (non-subscripted) channel use by evaluating its location
    and then adding it to the channel table and returning it as an element. 
    """
    #print(Printer().expr(stmt.location))
    location_value = EvalExpr().expr(stmt.location)
    tab.insert(name, None, location_value, chanend, chan_set)
    debug(self.debug, '  {} at {}'.format(name, location_value))
    return ChanElem(None, location_value, None, None)

  def subscript_channel(self, indicies, tab, stmt, name, expr, chanend, chan_set):
    """
    Expand the use of a channel subscript over a set of iterators and determine
    for each the value of its index and location, and then add this to the
    channel table and corresponding expansion.
    """
    #print(Printer().expr(stmt.location))
    chan_elems = []

    # Iterate over cartesian product of iterator ranges
    ranges = [range(x.base_value, x.base_value+x.count_value) for x in indicies]
    for x in product(*ranges):

      # Deep copy expressions so we can modify them
      index_expr = copy.deepcopy(expr)
      location_expr = copy.deepcopy(stmt.location)

      # Substitute index variables for values
      index_values = []
      for (y, z) in zip(indicies, x):
        index_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
        location_expr.accept(SubElem(ast.ElemId(y.name),
          ast.ElemNumber(z-y.base_value)))
        index_values.append(z)

      # Evaluate the expressions
      index_value = EvalExpr().expr(index_expr)
      location_value = EvalExpr().expr(location_expr)

      # Add to the table
      tab.insert(name, index_value, location_value, chanend, chan_set)

      # Add the expanded channel use to a list
      chan_elems.append(ChanElem(index_value, location_value, 
          indicies, index_values))

      debug(self.debug, '  {}[{}] at {}'.format(name, index_value, location_value))
    
    return chan_elems

  def expand_uses(self, tab, indicies, chan_uses, stmt):
    """
    For each channel use, expand it into a set of elements.
    """
    chans = []
    for x in chan_uses.uses:
      chanend = tab.new_chanend()
      if x.expr == None:
        chan_set = ChanElemSet(x.name, x.expr, x.symbol, indicies, chanend)
        chan_set.elems = [self.single_channel(
            tab, stmt, x.name, chanend, chan_set)]
        chans.append(chan_set)
      else:
        chan_set = ChanElemSet(x.name, x.expr, x.symbol, indicies, chanend)
        chan_set.elems = self.subscript_channel(
            indicies, tab, stmt, x.name, x.expr, chanend, chan_set)
        chans.append(chan_set)

    # Sort them by chanend
    chans = sorted(chans, key=lambda x: x.chanend)
    return chans
 
  def insert_chan_decls(self, tab, decls):
    """
    Insert the names of channels from a set of declarations in the current scope.
    """
    for x in decls:
      if x.type == T_CHAN_SINGLE:
        tab.insert(x.name, None, None, None, None, decl=True)
      elif x.type == T_CHAN_ARRAY:
        tab.insert(x.name, None, None, None, None, decl=True)
      else:
        pass

  def check_chan(self, name, index, chan_elem):
    """
    Check each ChanItem entry in the table is valid: contains both master and 
    one slave location. 
    """
    #print('Checking chan '+name+' {}'.format(index))
    c = '{}{}'.format(name, '' if index==None else '[{}]'.format(index) )
    if not chan_elem.locations:
      self.errorlog.report_warning('channel '+c+' is not used')
    elif len(chan_elem.locations) == 1:
      self.errorlog.report_error('channel '+c+' has no slave connection')
    # NOTE: this is valid with server connections
    #elif len(locations) > 2:
    #  self.errorlog.report_error('channel '+c+' has multiple slaves') 
    
  def check_chans(self, tab, decls):
    """
    Check each channel is used correctly by inspecting the entries in the
    channel table and label channel variables with unique identifiers.
    """
    for x in decls:
      if x.type == T_CHAN_SINGLE:
        self.check_chan(x.name, None, tab.lookup(x.name, None))
      elif x.type == T_CHAN_ARRAY:
        for y in range(x.symbol.value):
          if tab.contains(x.name, y): 
            self.check_chan(x.name, y, tab.lookup(x.name, y))
      else:
        pass

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================
  
  def defn(self, node):
    node.chantab = ChanTable(node.name)
    chan_uses = self.stmt(node.stmt, [], node.chantab)
    node.chans = self.expand_uses(node.chantab, [], chan_uses, node.stmt)

  # Statements ==========================================

  # Top-level statements where connections are inserted as we distribute on
  # these boundaries. The set use_instances contains all the unique occurances
  # of channels in the contained process.

  def stmt_rep(self, node, indicies, tab):
    indicies = indicies + node.indicies
    chan_uses = self.stmt(node.stmt, indicies, tab)
    node.chans = self.expand_uses(tab, indicies, chan_uses, node.stmt)

    # Display the channel table
    if DISPLAY_CHANTAB:
      tab.display()
    
    # Return no uses
    return ChanUseSet() 
  
  def stmt_par(self, node, indicies, tab):
    tab.begin_scope()
    self.insert_chan_decls(tab, node.decls)
    
    # For each statement in the par, group the expansions
    node.chans = []
    for x in node.stmt:
      chan_uses = self.stmt(x, indicies, tab)
      node.chans.append(self.expand_uses(tab, indicies, chan_uses, node))

    self.check_chans(tab, node.decls)
    node.scope = tab.end_scope()

    # Display the channel table
    if DISPLAY_CHANTAB:
      tab.display()
    
    # Return no uses 
    return ChanUseSet()
 
  def stmt_server(self, node, indicies, tab):
    tab.begin_scope()
    self.insert_chan_decls(tab, node.decls)
    node.chans = []
    chan_uses = self.stmt(node.server, indicies, tab)
    node.chans.append(self.expand_uses(tab, indicies, chan_uses, node))
    chan_uses = self.stmt(node.client, indicies, tab)
    node.chans.append(self.expand_uses(tab, indicies, chan_uses, node))
    self.check_chans(tab, node.decls)
    node.scope = tab.end_scope()
    
    # Display the channel table
    if DISPLAY_CHANTAB:
      tab.display()
    
    # Return no uses 
    return ChanUseSet()

  def stmt_on(self, node, indicies, tab):
    chan_uses = self.stmt(node.stmt, indicies, tab)
    node.chans = self.expand_uses(tab, indicies, chan_uses, node.stmt)
    
    # Display the channel table
    if DISPLAY_CHANTAB:
      tab.display()
    
    # Return no uses 
    return ChanUseSet()

  # Statements containing uses of channels ================

  def stmt_in(self, node, indicies, tab):
    c = node.left
    t = c.symbol.type
    debug(self.debug, 'out channel {}:'.format(c.name))
    
    if (isinstance(c, ast.ElemId) 
        and (t == T_CHAN_SINGLE or t == T_CHANEND_SINGLE)):
      return ChanUseSet([ChanUse(c.name, None, c.symbol)])
    
    elif (isinstance(c, ast.ElemSub)
       and (t == T_CHAN_ARRAY or t == T_CHANEND_ARRAY)):
        return ChanUseSet([ChanUse(c.name, c.expr, c.symbol)])
    
    else:
        return ChanUseSet()

  def stmt_out(self, node, indicies, tab):
    c = node.left
    t = c.symbol.type
    debug(self.debug, 'in channel {}:'.format(c.name))

    if (isinstance(c, ast.ElemId) 
        and (t == T_CHAN_SINGLE or t == T_CHANEND_SINGLE)):
      return ChanUseSet([ChanUse(c.name, None, c.symbol)])
    
    elif (isinstance(c, ast.ElemSub) and
        (t == T_CHAN_ARRAY or t == T_CHANEND_ARRAY)):
        return ChanUseSet([ChanUse(c.name, c.expr, c.symbol)])
    
    else:
        return ChanUseSet()

  def stmt_pcall(self, node, indicies, tab):
    uses = ChanUseSet()

    for x in node.args:
      if isinstance(x, ast.ExprSingle):

        if (isinstance(x.elem, ast.ElemId)
            and x.elem.symbol.type == T_CHAN_SINGLE):
          debug(self.debug, 'single arg channel {}:'.format(x.elem.name))
          uses.add(ChanUse(x.elem.name, None, c.elem.symbol))

        elif (isinstance(x.elem, ast.ElemSub)
            and x.elem.symbol.type == T_CHAN_ARRAY):
          debug(self.debug, 'subscript arg channel {}:'.format(x.elem.name))
          uses.add(ChanUse(x.elem.name, x.elem.expr, c.elem.symbol))

        else:
          pass

    return uses
    
  # Other statements containing processes =================

  def stmt_seq(self, node, indicies, tab):
    tab.begin_scope()
    self.insert_chan_decls(tab, node.decls)
    uses = ChanUseSet()
    [uses.update(self.stmt(x, indicies, tab)) for x in node.stmt]
    self.check_chans(tab, node.decls)
    node.scope = tab.end_scope()
    return uses

  def stmt_if(self, node, indicies, tab):
    uses = self.stmt(node.thenstmt, indicies, tab)
    uses.update(self.stmt(node.elsestmt, indicies, tab))
    return uses

  def stmt_while(self, node, indicies, tab):
    return self.stmt(node.stmt, indicies, tab)

  def stmt_for(self, node, indicies, tab):
    #indicies.append(node.index)
    return self.stmt(node.stmt, indicies, tab)

  # Statements not containing processes or channels uses ==

  def stmt_ass(self, node, indicies, tab):
    return ChanUseSet()

  def stmt_alias(self, node, indicies, tab):
    return ChanUseSet()

  def stmt_skip(self, node, indicies, tab):
    return ChanUseSet()

  def stmt_connect(self, node, indicies, tab):
    return ChanUseSet()

  def stmt_assert(self, node, indicies, tab):
    return ChanUseSet()

  def stmt_return(self, node, indicies, tab):
    return ChanUseSet()


# These classes represent uses of channels as they occur in the program

class ChanUse(object):
  """
  A channel use.
  """
  def __init__(self, name, expr, symbol):
    self.name = name
    self.expr = expr
    self.symbol = symbol

  def __eq__(self, x):
    if not self.expr:
      return self.name == x.name
    else:
      return (self.name == x.name and 
          CmpExpr().expr(self.expr, x.expr))

  def __ne__(self, x):
    return not self.__eq__(x)


class ChanUseSet(object):
  """
  A set of unique channel uses.
  """
  def __init__(self, init=[]):
    self.uses = []
    [self.add(x) for x in init]

  def add(self, use):
    if not any(x == use for x in self.uses):
      self.uses.append(use)

  def update(self, useset):
    [self.add(x) for x in useset.uses]


# These classes represent expanded uses of channels that occur in a program,
# i.e. for a channel subscript c[f(i, j)] all of the channels accessed by the
# index f over the index ranges referenced by i and j. For single channels,
# i.e. c, this set has one element.

class ChanElem(object):
  """
  An element of a channel expansion with:
   - An (integer) index value
   - The location of the use at the index (in order to retrieve the entry from
     the channel table).
   - The values of the iterators yeilding index.
  """  
  def __init__(self, index, location, indicies, index_values):
    self.index = index
    self.location = location
    self.indicies_value = None
    if indicies != None and index_values != None:
      self.indicies_value = indicies_value(indicies, index_values)


class ChanElemSet(object):
  """
  An expanded channel array subscript with the following attributes:
   - The array name
   - The subscript expression
   - A set of elements relating to the expansion, e.g. c[0], c[1], ...
   - The iterators used in the subscript.
   - The name of the channel end associated with this subscript.
  """
  def __init__(self, name, expr, symbol, indicies, chanend):
    self.name = name
    self.expr = expr
    self.symbol = symbol
    self.indicies = indicies
    self.chanend = chanend
    self.elems = None
    self.connid = None

