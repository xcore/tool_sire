# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import copy
import collections
from itertools import product

import ast
from walker import NodeWalker
from typedefs import *
from subelem import SubElem
from evalexpr import EvalExpr
from cmpexpr import CmpExpr

from printer import Printer

class LabelChans(NodeWalker):
  """
  For each procedure definition, construct a table which records for each use
  of a channel the locations of the master and slave processes (relative to the
  base). For replicators, expand array subscripts over the range of the
  iterators and tag each with its location. Then label each channel with the 
  relative offset from the master to the slave.
  """
  def __init__(self, device, errorlog, print_debug=False):
    self.device = device
    self.errorlog = errorlog
    self.print_debug = print_debug

  def debug(self, s):
    if self.print_debug:
      print(s)
  
  def single_channel(self, tab, stmt, name):
    """
    Process a single (non-subscripted) channel use by evaluating its location
    and then adding it to the channel table and returning it as an element. 
    """
    location_value = EvalExpr().expr(stmt.location)
    tab.insert(name, None, location_value)
    self.debug('  {} at {}'.format(name, location_value))
    return ChanElem(None, location_value)

  def subscript_channel(self, iters, tab, stmt, name, expr):
    """
    Expand the use of a channel subscript over a set of iterators and determine
    for each the value of its index and location, and then add this to the
    channel table and corresponding expansion.
    """
    #print(Printer().expr(elem.expr))
    #print(Printer().expr(stmt.location))
    chan_elems = []

    # Iterate over cartesian product of iterator ranges
    ranges = [range(x.base_value, x.base_value+x.count_value) for x in iters]
    for x in product(*ranges):

      # Deep copy expressions so we can modify them
      index_expr = copy.deepcopy(expr)
      location_expr = copy.deepcopy(stmt.location)

      # Substitute index variables for values
      for (y, z) in zip(iters, x):
        index_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))
        location_expr.accept(SubElem(ast.ElemId(y.name), ast.ElemNumber(z)))

      # Evaluate the expressions
      index_value = EvalExpr().expr(index_expr)
      location_value = EvalExpr().expr(location_expr)

      # Add to the table
      tab.insert(name, index_value, location_value)

      # Add the expanded channel use (name, index) to a list
      chan_elems.append(ChanElem(index_value, location_value))

      self.debug('  {}[{}] at {}'.format(name, index_value, location_value))
    
    return chan_elems

  def expand_uses(self, tab, iters, chan_uses, stmt):
    """
    For each channel use, expand it into a set of elements.
    """
    chans = []
    for x in chan_uses.uses:
      if x.expr == None:
        elems = [self.single_channel(tab, stmt, x.name)]
        chanend = tab.new_chanend()
        chans.append(ChanElemSet(x.name, x.expr, elems, chanend))
      else:
        elems = self.subscript_channel(iters, tab, stmt, x.name, x.expr)
        chanend = tab.new_chanend()
        chans.append(ChanElemSet(x.name, x.expr, elems, chanend))
    return chans
  
  def check_chan(self, name, index, locations):
    """
    Check each entry in the table is valid: contains both master and one slave
    location.
    """
    #print('Checking chan '+name+' {}'.format(index))
    c = '{}{}'.format(name, '' if index==None else '[{}]'.format(index) )
    if not locations:
      self.errorlog.report_warning('channel '+c+' is not used')
    elif len(locations) == 1:
      self.errorlog.report_error('channel '+c+' has no slave connection')
    elif len(locations) > 2:
      self.errorlog.report_error('channel '+c+' has multiple slaves') 

  # Program ============================================

  def walk_program(self, node):
    [self.defn(x) for x in node.defs]
  
  # Procedure definitions ===============================
  
  def defn(self, node):
    self.debug('New channel scope: '+node.name)
    node.chantab = ChanTable(node.name)
    chan_uses = self.stmt(node.stmt, [], node.chantab)
    node.chans = self.expand_uses(node.chantab, [], chan_uses, node.stmt)
    node.chanids = {}
    id_count = 0
    
    # Check each channel is used correctly by inspecting the entries in the
    # channel table and label channel variables with unique identifiers.
    for x in node.decls:
      if x.type == T_CHAN_SINGLE:
        self.check_chan(x.name, None, node.chantab.lookup(x.name, None))
        node.chanids[x.name] = id_count
        id_count += 1
      elif x.type == T_CHAN_ARRAY:
        for y in range(x.symbol.value):
          self.check_chan(x.name, y, node.chantab.lookup(x.name, y))
        node.chanids[x.name] = id_count
        id_count += 1
      else:
        pass

    # Resolve multiple connections on the same channel id
    # TODO: prove that this will terminate
    change = True
    while change:
      change = False
      #print('iteration')
      for x in filter(lambda x: x.type==T_CHAN_ARRAY, node.decls):
        core = [0]*self.device.num_cores() 
        for y in range(x.symbol.value):
          s = node.chantab.lookup_slave_location(x.name, y)
          if core[s] > 0:
            node.chantab.swap(x.name, y)
            s = node.chantab.lookup_slave_location(x.name, y)
            core[s] += 1
            if core[s] > 1:
              print('ERROR: multiple connections to slave {}'.format(s))
            change = True
          else:
            core[s] += 1
    
    # Display the channel table
    #node.chantab.display()
  
  # Statements ==========================================

  # Top-level statements where connections are inserted as we distribute on
  # these boundaries. The set use_instances contains all the unique occurances
  # of channels in the contained process.

  def stmt_rep(self, node, iters, tab):
    iters = iters + node.indicies
    chan_uses = self.stmt(node.stmt, iters, tab)
    node.chans = self.expand_uses(tab, iters, chan_uses, node.stmt)

    # Return no uses 
    return ChanUseSet()
      
  def stmt_par(self, node, iters, tab):
    
    # For each statement in the par, group the expansions
    node.chans = []
    for x in node.stmt:
      chan_uses = self.stmt(x, iters, tab)
      node.chans.append(self.expand_uses(tab, iters, chan_uses, node))
    
    # Return no uses 
    return ChanUseSet()
 
  # Statements containing uses of channels.

  def stmt_in(self, node, iters, tab):
    c = node.left
    t = c.symbol.type
    self.debug('out channel {}:'.format(c.name))
    
    if (isinstance(c, ast.ElemId) 
        and (t == T_CHAN_SINGLE or t == T_CHAN_ARRAY)):
      return ChanUseSet([ChanUse(c.name, None)])
    
    elif (isinstance(c, ast.ElemSub)
       and (t == T_CHAN_SINGLE or t == T_CHAN_ARRAY)):
        return ChanUseSet([ChanUse(c.name, c.expr)])
    
    else:
        return ChanUseSet()

  def stmt_out(self, node, iters, tab):
    c = node.left
    t = c.symbol.type
    self.debug('in channel {}:'.format(c.name))

    if (isinstance(c, ast.ElemId) 
        and (t == T_CHAN_SINGLE or t == T_CHAN_ARRAY)):

      return ChanUseSet([ChanUse(c.name, None)])
    
    elif (isinstance(c, ast.ElemSub)
       and (t == T_CHAN_SINGLE or t == T_CHAN_ARRAY)):
        return ChanUseSet([ChanUse(c.name, c.expr)])
    
    else:
        return ChanUseSet()

  def stmt_pcall(self, node, iters, tab):
    uses = ChanUseSet()
    for x in node.args:
      if isinstance(x, ast.ExprSingle):

        if (isinstance(x.elem, ast.ElemId)
            and x.elem.symbol.type == T_CHAN_SINGLE):
          self.debug('single arg channel {}:'.format(x.elem.name))
          uses.add(ChanUse(x.elem.name, None))

        elif (isinstance(x.elem, ast.ElemSub)
            and x.elem.symbol.type == T_CHAN_ARRAY):
          self.debug('subscript arg channel {}:'.format(x.elem.name))
          uses.add(ChanUse(x.elem.name, x.elem.expr))

        else:
          pass

    return uses
    
  # Other statements containing processes

  def stmt_seq(self, node, iters, tab):
    uses = ChanUseSet()
    [uses.update(self.stmt(x, iters, tab)) for x in node.stmt]
    return uses

  def stmt_if(self, node, iters, tab):
    uses = self.stmt(node.thenstmt, iters, tab)
    uses.update(self.stmt(node.elsestmt, iters, tab))
    return uses

  def stmt_while(self, node, iters, tab):
    return self.stmt(node.stmt, iters, tab)

  def stmt_for(self, node, iters, tab):
    return self.stmt(node.stmt, iters, tab)

  def stmt_on(self, node, iters, tab):
    return self.stmt(node.stmt, iters, tab)

  # Statements not containing processes or channels uses

  def stmt_ass(self, node, iters, tab):
    return ChanUseSet()

  def stmt_alias(self, node, iters, tab):
    return ChanUseSet()

  def stmt_skip(self, node, iters, tab):
    return ChanUseSet()

  def stmt_connect(self, node, iters, tab):
    return ChanUseSet()

  def stmt_assert(self, node, iters, tab):
    return ChanUseSet()

  def stmt_return(self, node, iters, tab):
    return ChanUseSet()


class ChanTable(object):
  """
  A table to record the location of channel ends and their names. Each key maps
  to list of locations where the first location is that of the master, and a 
  unique identifier for the specific connection instance.
  """
  def __init__(self, name):
    self.name = name
    self.tab = {}
    self.chanend_count = 0
    
  def key(self, name, index):
    """
    Given a channel name and its index return a key concatenating these.
    """
    return '{}{}'.format(name, '' if index==None else index)

  def insert(self, name, index, location):
    """
    Add a channel element with an index and location to the table.
    """
    key = self.key(name, index)
    if not key in self.tab:
      self.tab[key] = []
    self.tab[key].append(location)
    #print('inserted '+name+'[{}] @ {}'.format(index, location))

  def lookup(self, name, index):
    """
    Lookup a channel's master and slave location.
    """
    key = self.key(name, index)
    if not key in self.tab:
      return None
    return self.tab[key]

  def lookup_slave_location(self, name, index):
    key = self.key(name, index)
    assert key in self.tab and len(self.tab[key])==2
    return self.tab[key][1]

  def is_master(self, name, index, location):
    key = self.key(name, index)
    if key in self.tab:
      return self.tab[key][0] == location
    return None

  def swap(self, name, index):
    key = self.key(name, index)
    if key in self.tab:
      self.tab[key].reverse()

  def new_chanend(self):
    name = '_c{}'.format(self.chanend_count)
    self.chanend_count += 1
    return name

  def display(self):
    print('Channel table for procedure '+self.name+':')
    for x in self.tab.keys():
      print('  {} has {}'.format(x, ', '.join(
        ['{}'.format(y) for y in self.tab[x]])))


# These classes represent uses of channels as they occur in the program

class ChanUse(object):
  """
  A channel use.
  """
  def __init__(self, name, expr):
    self.name = name
    self.expr = expr

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
  """  
  def __init__(self, index, location):
    self.index = index
    self.location = location


class ChanElemSet(object):
  """
  An expanded channel array subscript with the following attributes:
   - The array name
   - The subscript expression
   - A set of elements relating to the expansion, e.g. c[0], c[1], ...
   - The name of the channel end associated with this subscript
  """
  def __init__(self, name, expr, elems, chanend):
    self.name = name
    self.expr = expr
    self.elems = elems
    self.chanend = chanend

