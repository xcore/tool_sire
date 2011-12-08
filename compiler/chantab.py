# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

from util import debug

class ChanTable(object):
  """
  A table to record the location of channel ends and their names. Each key maps
  to list of locations where the first location is that of the master, and a 
  unique identifier for the specific connection instance.
  """
  def __init__(self, name, debug=False):
    self.name = name
    self.debug = debug
    self.scopes = []
    self.chanend_count = 0
  
  def begin_scope(self):
    self.scopes.append(Scope(self.scopes[-1] if len(self.scopes)>0 else None))
    debug(self.debug, 'New scope')

  def end_scope(self):
    tab = self.scopes.pop()
    debug(self.debug, 'Ended scope')
    return tab

  def key(self, name, index):
    return '{}{}'.format(name, '' if index==None else index)

  def insert(self, name, index, location, chanend, chan_set, decl=False):
    """
    Add channel declarations (with just names) so channel uses can be added to
    the correct scope.
    Or add a channel element with a particular index into the table recording the
    location and the ChanElemSet it is a member of (this is necessary for
    performing colouring to assign connection ids).
    Declarations are prefixed with an underscore.
    """
    if decl:
      self.scopes[-1].tab['_'+name] = Channel()
      debug(self.debug, '  Insert decl: '+name)
      return
    else:
      scope = self.scopes[-1]
      while scope != None:
        if '_'+name in scope.tab:
          key = self.key(name, index)
          if not key in scope.tab:
            scope.tab[key] = Channel()
          scope.tab[key].locations.append(location)
          scope.tab[key].chanends.append(chanend)
          scope.tab[key].chan_sets.append(chan_set)
          debug(self.debug, '  Insert: '+name+'{} @ {}'.format(
              '[{}]'.format(index) if index!=None else '', location))
          return
        scope = scope.prev
    print('Could not insert element of channel '+name)
    assert 0

  def contains(self, name, index):
    """
    Check if the table contains a channel element.
    """
    return any(self.key(name, index) in x.tab for x in self.scopes)

  def lookup(self, name, index, base=None, scoped=False):
    """
    Lookup a channel's master and slave location. If base is set, a lookup can
    be made from any scope.
    """
    key = self.key(name, index)
    scope = self.scopes[-1] if base==None else base
    while scope != None:
      if key in scope.tab:
        debug(self.debug,"  Lookup: "+key)
        return scope.tab[key]
      scope = scope.prev
    return None

  def lookup_master_location(self, name, index, base=None):
    x = self.lookup(name, index, base)
    return x.locations[0] if x != None else None

  def lookup_slave_location(self, name, index, base=None):
    x = self.lookup(name, index, base)
    return x.locations[1] if x != None else None

  def lookup_chanset(self, name, index, master, base=None):
    x = self.lookup(name, index, base)
    return x.chan_sets[0 if master else 1] if x != None else None

  def lookup_is_master(self, name, index, chanend, base=None):
    x = self.lookup(name, index, base)
    return x.chanends[0] == chanend if x != None else None

  def new_chanend(self):
    name = '_c{}'.format(self.chanend_count)
    self.chanend_count += 1
    return name

  def display(self):
    print('Channel table for procedure '+self.name+':')
    print('--------------------------')
    for x in self.scopes:
      if len(x.tab) == 0:
        print('  Empty')
      for y in x.tab.keys():
        print('  Channel {} is {}'.format(y, x.tab[y]))
      print('--------------------------')


class Scope(object):
  """
  A scope represented by a table of channel identifiers with a pointer to the
  previous scope.
  """
  def __init__(self, prev):
    self.tab = {}
    self.prev = prev


class Channel(object):
  """
  A channel entity.
  """
  def __init__(self):
    self.connid = None
    self.locations = []
    self.chanends = []
    self.chan_sets = []
  
  def __repr__(self):
    return 'locations: {}, chanends: {}'.format(
        ', '.join(['{}'.format(x) for x in self.locations]),
        ', '.join(['{}'.format(x) for x in self.chanends]))

