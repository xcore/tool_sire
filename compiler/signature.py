# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import definitions as defs
from typedefs import * 

class SignatureTable(object):
  """
  A procedure signature table.
  """
  def __init__(self, errorlog, debug=False):
    self.errorlog = errorlog
    self.debug = debug
    self.tab = {}
    self.mobile_proc_names = []
    self.mobile_proc_marks = {} # This is pretty wasteful
    self.id_count = 0

  def insert(self, type, node, mobile=True):
    """
    Insert a procedure signature, mobile denotes if it will be added to the
    jump table and be mobile between cores.
    """
    if not node.name in self.tab:
     
      # Check the number of formal parameters
      if (node.formals and len(node.formals) > defs.MAX_PROC_PARAMETERS):
        self.errorlog.report_error(
            "procedure '{}' exceeds maximum ({}) number of formals: {}"
            .format(node.name, defs.MAX_PROC_PARAMETERS,
              len(node.formals)))
        return False
       
      # Create and insert the signature
      self.tab[node.name] = Signature(node.name, type, node.formals)
       
      # Add it to the list of mobiles if it is mobile
      if mobile:
        self.mobile_proc_names.append(node.name)
        self.mobile_proc_marks[node.name] = False
        #print('Added mobile '+node.name)
      
      if(self.debug):
        print("Inserted sig for '{}' {}".format(node.name, type))
      
    return True

  def remove(self, name):
    """
    Delete an entry with key name.
    """
    if name in self.tab:
      s = self.tab[name] 
      del self.tab[name]
      if name in self.mobile_proc_names:
        self.mobile_proc_names.remove(name)
      if(self.debug):
        print("Deleted sig for '{}' ({})".format(s.name, s.type))
      return True
    else:
      return False

  def mark(self, name):
    """
    Mark a procedure. It will not appear in the table if it is a non-mobile
    builtin such as the printing functions.
    """
    assert name in self.tab
    if name in self.mobile_proc_marks:
      self.mobile_proc_marks[name] = True

  def remove_unused(self):
    used = []
    [used.append(x) for x in self.mobile_proc_names if self.mobile_proc_marks[x]]
    self.mobile_proc_names = used

  #def lookup_param_type(self, name, i):
  #  """
  #  Given a procedure name and an index, return the formal type.
  #  """
  #  return self.tab[name].params[i].type

  def lookup_array_qualifier(self, name, i):
    """ 
    Given the index of an array parameter, return the index of the
    qualifying paramemer in the ordered set of formal parameters.
    """
    params = self.tab[name].params
    assert(params[i].type == T_REF_ARRAY) 
    
    qualifier = params[i].expr.elem.name
    for (i, x) in enumerate(params):
      if x.name == qualifier: return i
    
    return None

  def has_channel_params(self, name):
    def chanend_param(f):
      return f.symbol.type == T_CHANEND_SINGLE or \
          f.symbol.type == T_CHANEND_ARRAY or \
          f.symbol.type == T_CHAN_SINGLE or \
          f.symbol.type == T_CHAN_ARRAY
    if name in self.tab:
      return any([chanend_param(x) for x in self.tab[name].params])

  def is_mobile(self, name):
    """
    Return if a procedure name is mobile, i.e. it is defined in the source of
    the program.
    """
    return name in self.mobile_proc_names
  
  def sig_exists(self, name):
    """
    Return the list of formal parameter declarations for a named procedure.
    """
    return name in self.tab

  def get_params(self, name):
    """
    Return the list of formal parameter declarations for a named procedure.
    """
    return self.tab[name].params if name in self.tab else None

  def add_mobile_proc(self, name):
    """
    Add a process to the list of mobiles.
    """
    self.mobile_proc_names.append(name)

  def unique_process_name(self):
    name = '_p{}'.format(self.id_count)
    self.id_count = self.id_count + 1
    return name

  def dump(self, buf=sys.stdout):
    """
    Dump the contents of the table to buf.
    """
    [buf.write(repr(x)) for x in self.scope]


class Signature(object):
  """
  A procedure signature.
  """
  def __init__(self, name, type, params):
    self.name = name
    self.type = type
    self.params = params

  def __repr__(self):
    return '{} {} {}'.format(self.name, self.type, ', '.join(
      [x.type for x in self.params]))

