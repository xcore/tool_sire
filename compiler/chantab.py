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
  def __init__(self, name, debug=True):
    self.name = name
    self.debug = debug
    self.scopes = []
    self.chan_count = 0
    self.chanend_count = 0
  
  def begin_scope(self):
    self.scopes.append({})
    debug(self.debug, 'New scope')

  def end_scope(self):
    tab = self.scopes.pop()
    del tab
    debug(self.debug, 'Ended scope')

  def key(self, name, index):
    return '{}{}'.format(name, '' if index==None else index)

  def insert(self, name, index, location, chan_set):
    """
    Add a channel element with a particular index into the table recording the
    location and the ChanElemSet it is a member of (this is necessary for
    performing colouring to assign connection ids).
    """
    key = self.key(name, index)
    if not key in self.scopes[-1]:
      self.scopes[-1][key] = Channel()
    self.scopes[-1][key].locations.append(location)
    self.scopes[-1][key].chan_sets.append(chan_set)
    debug(self.debug, '  Insert: '+name+'{} @ {}'.format(
      '[{}]'.format(index) if index else '', location))

  def contains(self, name, index):
    """
    Check if the table contains a channel element.
    """
    return any(self.key(name, index) in x for x in self.scopes)

  def lookup(self, name, index):
    """
    Lookup a channel's master and slave location.
    """
    key = self.key(name, index)
    for x in reversed(self.scopes):
      if key in x:
        debug(self.debug,"  Lookup: "+key)
        return x[key] 
    return None

  def lookup_master_location(self, name, index):
    x = lookup(name, index)
    return x.locations[0] if x != None else None

  def lookup_slave_location(self, name, index):
    x = lookup(name, index)
    return x.locations[1] if x != None else None

  def lookup_chanset(self, name, index, master):
    x = lookup(name, index)
    return x.chan_sets[0 if master else 1] if x != None else None

  def is_master(self, name, index, location):
    x = lookup(name, index)
    return self.tab[key].locations[0] == location if x != None else None

  def get_next_chan_id(self):
    x = self.chanend_count
    self.chanend_count += 1
    return x

  def new_chanend(self):
    name = '_c{}'.format(self.chanend_count)
    self.chanend_count += 1
    return name

  def display(self):
    print('Channel table for procedure '+self.name+':')
    for x in self.tab.keys():
      print('  channel {} is {}'.format(x, self.tab[x]))


class Channel(object):
  """
  A channel entity.
  """
  def __init__(self):
    self.connid = None
    self.locations = []
    self.chan_sets = []
  
  def __repr__(self):
    return 'locations: {}'.format(
        ', '.join(['{}'.format(x) for x in self.locations]))

