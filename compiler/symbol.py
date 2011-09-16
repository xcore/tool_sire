# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from typedefs import *

scopes = [
  T_SCOPE_SYSTEM, 
  T_SCOPE_PROGRAM,
  T_SCOPE_PROC,
  T_SCOPE_FUNC,
  ]

class SymbolTable(object):
  """ 
  Symbol table.
  """
  def __init__(self, error, debug=False):
    self.error = error
    self.debug = debug
    self.scope = []
    self.tab = {}

  def begin_scope(self, tag):
    """ 
    Begin a new scope.
    """
    s = ScopeTag(tag)
    self.scope.append(s)
    self.curr_scope = tag
    if(self.debug): 
      print("New scope '{}'".format(s.name))

  def end_scope(self, warn_unused=True):
    """ 
    End a scope.
    """
    s = None
    while not (self.scope[-1].type.isTag()):
      s = self.scope.pop()
      #del self.tab[s.name]
      if(self.debug): 
        print("Popped sym '{}' with type {}".format(s.name, s.type))

      # If symbol hasn't been used, give a warning
      if not s.mark and not s.name == defs.LABEL_MAIN and warn_unused:
        self.error.report_warning(
            "variable '{}' declared but not used"
            .format(s.name))
    
    s = self.scope.pop()
    self.curr_scope = self.get_curr_scope()
    if(self.debug): 
      print("Ended scope '{}', new scope '{}'"
        .format(s.name, self.curr_scope))
   
  def get_curr_scope(self):
    """ 
    Traverse scope stack from top to bottom to find first scope tag.
    """
    for x in reversed(self.scope):
      if x.type.isTag():
        return x.name

  def insert(self, name, type, expr=None, coord=None):
    """ 
    Insert a new symbol in the table.
    """
    s = Symbol(name, type, expr, coord, self.curr_scope)
    self.tab[name] = s 
    self.scope.append(self.tab[name])
    if(self.debug):
      print("Inserted sym '{}' {} in scope '{}'"
          .format(name, type, self.curr_scope))
    return s

  #def insert_scoped(self, name, type, expr=None, coord=None):
  #  """ Insert a new symbol in the table if it doesn't already exist in the
  #    current scope.
  #  """
  #  if not self.lookup_scoped(name):
  #    return self.insert(name, type, expr, coord)
  #  return None

  # TODO: ideally, symbol lookup should be O(1) by creating new tables for
  # each new scope
  def lookup(self, key):
    """ 
    Lookup a symbol in scope order.
    """
    for x in reversed(self.scope):
      if x.name == key: 
        return x
    #if self.debug:
    #  print('Lookup: '+key+' found {}'.format(symbol))
    #print('didnt find symbol: '+key)
    return None

  def lookup_scoped(self, key):
    """ 
    Lookup a symbol in the current scope.
    """
    for x in reversed(self.scope):
      if x.type.isTag(): return None
      if x.name == key: return x

  def check_decl(self, key):
    """ 
    Check a symbol has been declared.
    """
    s = self.lookup(key) 
    #print("check decl: "+key+" is {}".format(not s == None))
    return not s == None

  def check_form(self, key, forms):
    """ 
    Check a symbol has been declared with the correct form.
    """
    if key in self.tab:
      return any(x == self.tab[key].type.form for x in forms)
    return False

  def check_type(self, key, types):
    """ 
    Check a symbol has been declared with the correct form.
    """
    if key in self.tab:
      return any(x == self.tab[key].type for x in types)
    return False

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

