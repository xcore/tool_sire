# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from util import debug
from typedefs import *

scopes = [
  T_SCOPE_SYSTEM, 
  T_SCOPE_PROGRAM,
  T_SCOPE_PROC,
  T_SCOPE_BLOCK,
  T_SCOPE_SERVER,
  T_SCOPE_CLIENT,
  ]

TAG = 0
TAB = 1

class SymbolTable(object):
  """ 
  Symbol table. 'scopes' maintains a list of tables, one for each scope.
  """
  def __init__(self, error, debug=False):
    self.error = error
    self.debug = debug
    self.scopes = []

  def begin_scope(self, tag):
    self.scopes.append((tag, {}))
    debug(self.debug, "New scope '{}'".format(tag))

  def end_scope(self, warn_unused=True):
    """
    End a scope, check for unused variables.
    """
    for x in self.scopes[-1][TAB].keys():
      s = self.scopes[-1][TAB][x]
      debug(self.debug, "  Popped '{}' type {}".format(s.name, s.type))

      # If symbol hasn't been used, give a warning
      if not s.mark and warn_unused:
        self.error.report_warning("'{}' declared but not used".format(s.name))
   
    tab = self.scopes.pop()
    del tab 
    debug(self.debug, "Ended scope, new scope '{}'".format(self.scopes[-1][0]))
   
  def insert(self, name, type, expr=None, coord=None):
    """ 
    Insert a new symbol in the table.
    """
    sym = Symbol(name, type, expr, coord, self.scopes[-1][TAG])
    self.scopes[-1][TAB][name] = sym
    debug(self.debug, "  Insert: '{}' {} in scope '{}'"
          .format(name, type, self.scopes[-1][TAG]))
    return sym

  def lookup(self, key):
    """ 
    Lookup a symbol in scope order.
    """
    for (tag, tab) in reversed(self.scopes):
      if key in tab:
        debug(self.debug,"  Lookup: "+key+" in scope '{}'".format(tag))
        return tab[key]
    return None

  def lookup_scoped(self, key):
    """ 
    Lookup a symbol in the current scope.
    """
    if key in self.scopes[-1][TAB]: 
      return self.scopes[-1][TAB][key]
    else:
      return None

  def check_decl(self, key):
    """ 
    Check a symbol has been declared.
    """
    s = self.lookup(key) 
    return not s == None

  def check_form(self, key, forms):
    """ 
    Check a symbol has been declared with the correct form.
    """
    sym = self.lookup(key)
    if sym == None:
      return False
    return any(x == sym.type.form for x in forms)

  def check_type(self, key, types):
    """ 
    Check a symbol has been declared with the correct form.
    """
    sym = self.lookup(key)
    if sym == None:
      return False
    return any(x == sym.type for x in types)

  def dump(self, buf=sys.stdout):
    """ 
    Dump the contents of the table to buf.
    """
    for x in self.scope:
      buf.write(repr(x))


class Symbol(object):
  """ 
  A generic symbol with a name, type and scope.
  """
  def __init__(self, name, type, expr=None, coord=None, scope=None):
    self.name = name
    self.type = type
    self.expr = expr
    self.coord = coord
    self.scope = scope
    self.value = None      # If it is a 'val', its actual value.
    self.mark = False      # Whether it has been used
    self.prototype = True  # If it's a prototype and not a definition

  def set_value(self, v):
    self.value = v
  
  def mark_used(self):
    self.mark = True

  def mark_prototype(self):
    self.prototype = True

  def unmark_prototype(self):
    self.prototype = False

  def __repr__(self):
    return '{}: {}'.format(self.name, self.type)


class ScopeTag(Symbol):
  """
  A scope tag symbol.
  """
  def __init__(self, name):
    super(ScopeTag, self).__init__(name, T_TAG, None, None, '')

