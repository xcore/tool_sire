# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys
import traceback
import error
import util
import definitions as defs
import ast
from util import debug
from walker import NodeWalker
from builtin import builtins
from typedefs import *
from evalexpr import EvalExpr
from printer import Printer

elem_types = {
  'elem_id'          : None,
  'elem_sub'         : None,
  'elem_slice'       : None,
  'elem_index_range' : None,
  'elem_group'       : None,
  'elem_fcall'       : T_VAR_SINGLE,
  'elem_number'      : T_VAL_SINGLE,
  'elem_boolean'     : T_VAL_SINGLE,
  'elem_string'      : T_VAR_ARRAY,
  'elem_char'        : T_VAL_SINGLE,
  }

# Valid actual parameter types that can be taken by each formal type.
param_conversions = {
  
  T_VAL_SINGLE : [
    T_VAL_SINGLE, 
    T_VAR_SINGLE, 
    T_REF_SINGLE, 
    T_VAR_SUB,
    T_REF_SUB,
    ],

  T_REF_SINGLE : [
    T_VAR_SINGLE, 
    T_REF_SINGLE, 
    T_VAR_SUB,
    T_REF_SUB,
    ],

  T_REF_ARRAY : [
    T_VAR_ARRAY, 
    T_REF_ARRAY, 
    ],

  T_CHANEND_SINGLE : [
    T_CHANEND_SINGLE,
    T_CHANEND_SUB,
    T_CHANEND_SERVER_SINGLE,
    T_CHANEND_CLIENT_SINGLE,
    T_CHAN_SINGLE,
    T_CHAN_SUB,
    ],

  T_CHANEND_SERVER_SINGLE : [
    T_CHANEND_SERVER_SINGLE,
    T_CHAN_SINGLE,
    T_CHAN_SUB,
    ],

  T_CHANEND_CLIENT_SINGLE : [
    T_CHANEND_CLIENT_SINGLE,
    T_CHAN_SINGLE,
    T_CHAN_SUB,
    ],

  T_CHANEND_ARRAY : [
    T_CHANEND_ARRAY,
    T_CHAN_ARRAY,
    ],
}

# Relation of variable types to formal parameter types for parallel composition.
par_var_to_param = {
  T_VAL_SINGLE            : T_VAL_SINGLE,
  T_VAR_SINGLE            : T_REF_SINGLE, 
  T_REF_SINGLE            : T_REF_SINGLE,
  T_VAR_SUB               : T_VAL_SINGLE,
  T_REF_SUB               : T_VAL_SINGLE,
  T_VAR_ARRAY             : T_REF_ARRAY, 
  T_REF_ARRAY             : T_REF_ARRAY,
  T_CHANEND_SINGLE        : T_CHANEND_SINGLE,
  T_CHANEND_SERVER_SINGLE : T_CHANEND_SERVER_SINGLE,
  T_CHANEND_CLIENT_SINGLE : T_CHANEND_CLIENT_SINGLE,
}

# Relation of variable types to formal parameter types for parallel replication.
# All singles map to values as there can be no single assignment in a
# replicator.
rep_var_to_param = {
  T_VAL_SINGLE            : T_VAL_SINGLE,
  T_VAR_SINGLE            : T_VAL_SINGLE, 
  T_REF_SINGLE            : T_VAL_SINGLE,
  T_VAR_SUB               : T_VAL_SINGLE,
  T_REF_SUB               : T_VAL_SINGLE,
  T_VAR_ARRAY             : T_REF_ARRAY, 
  T_REF_ARRAY             : T_REF_ARRAY,
  T_CHANEND_SINGLE        : T_CHANEND_SINGLE,
  T_CHANEND_SERVER_SINGLE : T_CHANEND_SERVER_SINGLE,
  T_CHANEND_CLIENT_SINGLE : T_CHANEND_CLIENT_SINGLE,
}

class Semantics(NodeWalker):
  """ 
  An AST walker class to check the semantics of a sire program.
  """
  def __init__(self, sym, sig, device, errorlog, debug=False):
    self.sym = sym
    self.sig = sig
    self.errorlog = errorlog
    self.debug = debug
    
    # Initialise variables in the 'system' scope
    
    # Add system variables core, chan
    self.sym.begin_scope('system')
    s = self.sym.insert(defs.SYS_NUM_CORES_CONST, T_VAL_SINGLE)
    s.set_value(device.num_cores())

    # Add all mobile builtin functions
    for x in builtins.values():
      self.sym.insert(x.definition.name, x.definition.type)
      self.sig.insert(x.definition.type, x.definition, x.mobile)

  def get_elem_type(self, elem):
    """ 
    Given an element, return its type
    """
    assert isinstance(elem, ast.Elem)

    # If its an expression group, get_expr_type
    if isinstance(elem, ast.ElemGroup):
      return self.get_expr_type(elem.expr)
    
    # If its a single identifer, look it up (if it exists)
    elif isinstance(elem, ast.ElemId):
      s = self.sym.lookup(elem.name)
      if s: 
        return s.type
      else:
        self.nodecl_error(elem.name)
        return None
    
    # If its a subscripted identifier, lookup and return subscripted type
    elif isinstance(elem, ast.ElemSub):
      s = self.sym.lookup(elem.name)
      if s:
        #print(s.type.subscriptOf())
        return s.type.subscriptOf()
      else:
        self.nodecl_error(elem.name)
        return None

    # If it is an array slice
    elif isinstance(elem, ast.ElemSlice):
      s = self.sym.lookup(elem.name)
      if s:
        return s.type
      else:
        self.nodecl_error(elem.name)
        return None

    # Otherwise, return the specified elem type
    else:
      return elem_types[util.camel_to_under(elem.__class__.__name__)]

  def get_expr_type(self, expr):
    """ 
    Given an expression work out its type
    """
    
    #If it's a single value, lookup the type
    if isinstance(expr, ast.ExprSingle):
      return self.get_elem_type(expr.elem) 
    
    # Otherwise it must be a unary or binop, and hence a var
    return T_VAR_SINGLE

  def check_elem_types(self, elem, types):
    """ 
    Given an elem and a set of types, check if one matches
    """
    t = self.get_elem_type(elem)
    #print('type {}'.format(t))
    return True if t and any([x==t for x in types]) else False

  def check_def(self, node):
    """ 
    Check if a procedure signature is defined for a [pf]call AST node.
    """
    
    # Compare each param type to the type of each expr argument
    debug(self.debug, 'Checking args for {}'.format(node.name))
    
    # Check the signature exists.
    if not self.sig.sig_exists(node.name):
      self.nodef_error(node.name, node.coord)
      return False

    # Check there is the right number
    if len(self.sig.get_params(node.name)) != len(node.args):
      self.nodef_error(node.name, node.coord)
      return False
    
    # Check the type of each actual matches the formal
    for (x, y) in zip(self.sig.get_params(node.name), node.args):
      t = self.get_expr_type(y)
      debug(self.debug, '  Arg type: {}, param type: {}'.format(t, x.type))

      # If argument y has no type, i.e. not defined
      if not t:
        self.nodef_error(node.name, node.coord)
        debug(self.debug, 'No type for argument')
        return False

      # Check it against each valid conversion
      if not any(t==z for z in param_conversions[x.type]):
        self.nodef_error(node.name, node.coord)
        debug(self.debug, 'No valid conversion')
        return False
    
    return True
  
  def check_decl(self, name, coord=None):
    """
    Check a symbol has been declared. If it has then mark it as used.
    """
    if self.sym.check_decl(name):
      symbol = self.sym.lookup(name)
      symbol.mark_used()
      return symbol
    else:
      self.nodecl_error(name, coord)
      return None

  def eval_expr(self, expr):
    """
    Evaluate a constant expession, cause an error if this is not possible.
    """
    v = EvalExpr().expr(expr)
    if v == None:
      self.non_const_error(expr)
    else:
      return v

  # Errors and warnings =================================

  def nodecl_error(self, name, coord=None):
    """ 
    No declaration.
    """
    self.errorlog.report_error(
        "'{}' not declared"
        .format(name), coord)

  def nodef_error(self, name, coord):
    """ 
    No definition.
    """
    self.errorlog.report_error(
        "no definition for '{}' "
        .format(name), coord)

  def redecl_error(self, name, coord):
    """
    Re-declaration
    """
    self.errorlog.report_error(
        "variable '{}' already declared in scope"
        .format(name), coord)

  def redef_error(self, name, coord):
    """ 
    Re-definition
    """
    self.errorlog.report_error(
        "procedure '{}' already declared"
        .format(name), coord)

  def procedure_def_error(self, name, coord):
    """ 
    Re-definition.
    """
    self.errorlog.report_error(
        "procedure '{}' definition invalid"
        .format(name), coord)

  def type_error(self, msg, name, coord):
    """ 
    Mismatching type.
    """
    self.errorlog.report_error(
        "type error in {} with '{}'"
        .format(msg, name), coord)

  def form_error(self, msg, name, coord):
    """ 
    Mismatching form.
    """
    self.errorlog.report_error(
        "form error in {} with '{}'"
        .format(msg, name), coord)

  def non_const_error(self, expr):
    """
    Constant expression cannot be evaluated.
    """
    self.errorlog.report_error("non-constant in expr: {}"
        .format(Printer().expr(expr)))

  def array_param_bound_decl_error(self, name, coord):
    """ 
    Array parameter length declaration is not constant or referenced by a
    single variable parameter.
    """
    self.errorlog.report_error(
        "invalid array length for '{}'"
        .format(name), coord)
      
  def input_target_error(self, coord):
    """ 
    Input statement target must be a single element.
    """
    self.errorlog.report_error("invalid input target", coord)

  def index_range_error(self, elem, coord):
    """ 
    Invald index range element.
    """
    self.errorlog.report_error("invalid index range: {}"
        .format(Printer().elem(elem), coord))

  def index_count_error(self, value, coord):
    """ 
    Invald index count (<= 0).
    """
    self.errorlog.report_error("index count value: {}".format(value), coord)

  def server_decls_error(self, coord):
    """ 
    Server declarations contain non-channel type.
    """
    self.errorlog.report_error("server channels", coord)

  # Program ============================================

  def walk_program(self, node):
    """
    Walk the progrm in a global 'program' scope. Don't close this so that
    symbols for any declared values remain accessible. 
    """
    self.sym.begin_scope(T_SCOPE_PROGRAM)
    [self.val_def(x) for x in node.decls]
    [self.proc_def(x) for x in node.defs]

    # Remove any unused procedures from the signature table. This is to stop
    # unused builtin functions from appearing unneccesarily in the jumptable.
    self.sig.remove_unused()

    # Leave the program scope open so values remain in scope of transformed
    # procedures.
    
  # Value definitons  ===============================

  def val_def(self, node):

    # Children
    self.expr(node.expr)
    
    # Check the symbol doesn't already exist in scope
    if not self.sym.lookup_scoped(node.name):
      s = self.sym.insert(node.name, node.type, node.expr, node.coord)
      node.symbol = s
    else:
      self.redecl_error(node.name, node.coord)

    # Determine the value of the expr
    node.symbol.value = self.eval_expr(node.expr)

  # Variable declarations ===============================

  def decl(self, node):

    # Children
    if node.expr:
      self.expr(node.expr)
    
    # Check the symbol doesn't already exist in scope
    if not self.sym.lookup_scoped(node.name):
      s = self.sym.insert(node.name, node.type, node.expr, node.coord)
      node.symbol = s
    else:
      self.redecl_error(node.name, node.coord)

    # If it's a value or array, then determine the value of the expr 
    if (node.type == T_VAR_ARRAY
       or node.type == T_CHAN_ARRAY):
      node.symbol.value = self.eval_expr(node.expr)

  # Procedure definitions ===============================

  def proc_def(self, node):
    
    # Rename main to avoid conflicts in linking
    if node.name == 'main':
      node.name = '_'+node.name

    # Add symbol and signature if it hasn't been declared
    s = self.sym.lookup_scoped(node.name)
    if not s:
      s = self.sym.insert(node.name, node.type, coord=node.coord)
      if not self.sig.insert(node.type, node):
        self.procedure_def_error(node.name, node.coord)
    # If it has been declared.
    else:
      if not s.prototype:
        self.redecl_error(node.name, node.coord)

    # Mark the main procedure in the signature table
    if node.name == '_main':
      self.sig.mark('_main')
      
    self.sym.begin_scope(T_SCOPE_PROGRAM)
    
    # First obtain all the symbols so that we can resolve all array length
    # specifiers, i.e. where the specifier appears before the array parameter.
    [self.param_pass1(x) for x in node.formals]
    [self.param_pass2(x) for x in node.formals]
     
    # Check if this is a prototype or the actual definition
    if node.stmt:
      
      # If there was a prototype, unmark it
      s.unmark_prototype()

      # Add the procedure name to the list
      self.parent = node.name
    
      # Body statement
      self.stmt(node.stmt)
  
    self.sym.end_scope()

  # Formals =============================================
  
  def param_pass1(self, node):

    # Check the declaration and add create the symbol
    if not self.sym.lookup_scoped(node.name):
      s = self.sym.insert(node.name, node.type, node.expr, node.coord)
      node.symbol = s
    else:
      self.redecl_error(node.name, node.coord)

  def param_pass2(self, node):

    # Children
    if node.type == T_REF_ARRAY or node.type == T_CHANEND_ARRAY:
      self.expr(node.expr)

    # Try and determine the array bound (if it's constant valued)
    if node.type == T_REF_ARRAY or node.type == T_CHANEND_ARRAY:
      node.symbol.value = EvalExpr().expr(node.expr)
      #print(node.name+' = {}'.format(node.symbol.value))

      # If it's not constant-valued, then check it's a single variable.
      if (node.symbol.value == None
          and not isinstance(node.expr, ast.ExprSingle)):
        self.array_param_bound_decl_error(node.name, node.coord)

  # Statements ==========================================

  def stmt_seq(self, node):
    self.sym.begin_scope(T_SCOPE_BLOCK)
    [self.decl(x) for x in node.decls]
    [self.stmt(x) for x in node.stmt]
    self.sym.end_scope()
      
  def stmt_par(self, node):
    self.sym.begin_scope(T_SCOPE_BLOCK)
    [self.decl(x) for x in node.decls]
    [self.stmt(x) for x in node.stmt]
    self.sym.end_scope()
      
  def stmt_server(self, node):

    # Check each declaration is a channel and *is not declared in any other
    # scope* because this will break the (simple implementation of the) channel
    # table for connection insertion.
    for x in node.decls:
      if not (x.type == T_CHAN_SINGLE or x.type == T_CHAN_ARRAY):
        self.server_decls_error(node.coord)
      else:
        if self.sym.lookup(x.name) != None:
          self.redecl_error(x.name, x.coord)

    # Children
    self.sym.begin_scope(T_SCOPE_SERVER)
    [self.decl(x) for x in node.decls]
    self.stmt(node.server)
    self.sym.end_scope()
    self.sym.begin_scope(T_SCOPE_CLIENT)
    [self.decl(x) for x in node.decls]
    self.stmt(node.client)
    self.sym.end_scope()

  def stmt_rep(self, node):
    
    # Children
    [self.elem(x) for x in node.indices]
    self.stmt(node.stmt)
    
    # Check all index elements are ElemIndexRanges
    for x in node.indices:
      if not isinstance(x, ast.ElemIndexRange):
        self.index_range_error(x, node.coord)
      
    # Determine the values of the base and count expressions and mark the index
    # ranges as distributed.
    for x in node.indices:
      x.distributed = True
      x.base_value = self.eval_expr(x.base)
      x.count_value = self.eval_expr(x.count)
      if x.count_value <= 0:
        self.index_count_error(x.count_value, node.coord)

  def stmt_skip(self, node):
    pass

  def stmt_pcall(self, node):

    # Children
    [self.expr(x) for x in node.args]

    # Check the decl and def
    node.symbol = self.check_decl(node.name, node.coord)
    self.check_def(node)
    
    # Mark the procedure as used in the signature table
    self.sig.mark(node.name)

    # TODO: check actual-formal types match, e.g. with refs.

  def stmt_ass(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for assignment target
    if not self.check_elem_types(node.left, [
         T_VAR_SINGLE, 
         T_REF_SINGLE, 
         T_VAR_SUB,
         T_REF_SUB,]):
      self.type_error('assignment', node.left.name, node.coord)

  def stmt_in(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for channel target
    if not self.check_elem_types(node.left, [
         T_CHAN_SINGLE, 
         T_CHAN_SUB,
         T_CHANEND_SINGLE, 
         T_CHANEND_SERVER_SINGLE, 
         T_CHANEND_CLIENT_SINGLE, 
         T_CHANEND_SUB,]):
      self.type_error('input channel', node.left.name, node.coord)

    # Check the input target is a single element
    if not isinstance(node.expr, ast.ExprSingle):
      self.input_target_error(node.coord)

    # Check valid type for input target
    if not self.check_elem_types(node.expr.elem, [
         T_VAR_SINGLE, 
         T_REF_SINGLE, 
         T_VAR_SUB,
         T_REF_SUB,]):
      self.type_error('input target', node.left.name, node.coord)

  def stmt_out(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for channel target
    if not self.check_elem_types(node.left, [
         T_CHAN_SINGLE, 
         T_CHAN_SUB,
         T_CHANEND_SINGLE, 
         T_CHANEND_SERVER_SINGLE, 
         T_CHANEND_CLIENT_SINGLE, 
         T_CHANEND_SUB,]):
      self.type_error('output channel', node.left.name, node.coord)

  def stmt_alias(self, node):

    # Children
    self.elem(node.left)
    self.elem(node.slice)

    # Check the target variable type
    if not self.check_elem_types(node.left, [T_REF_ARRAY]):
      self.type_error('array', node.left, node.coord)
    
    # Check the element is a slice
    if not isinstance(node.slice, ast.ElemSlice):
      self.slice_error('alias', node.coord)

  def stmt_connect(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.id)
    self.expr(node.expr)

    # Check the type of the chan element
    if not self.check_elem_types(node.left, [
        T_CHAN_SINGLE, 
        T_CHAN_SUB, 
        T_CHANEND_SINGLE, 
        T_CHANEND_SERVER_SINGLE, 
        T_CHANEND_CLIENT_SINGLE]):
      self.type_error('connect source channel', node.left, node.coord)

  def stmt_if(self, node):

    # Children
    self.expr(node.cond)
    self.stmt(node.thenstmt)
    self.stmt(node.elsestmt)

  def stmt_while(self, node):

    # Children
    self.expr(node.cond)
    self.stmt(node.stmt)

  def stmt_for(self, node):
       
    # Children
    self.elem(node.index)
    self.stmt(node.stmt)

    # Check the index is an ElemIndexRange
    if not isinstance(node.index, ast.ElemIndexRange):
      self.index_range_error(node.index, node.coord)
   
    # Mark the index range as non-distributed
    node.index.distributed = False

    # Determine the values of the base and count expressions
    #node.index.base_value = self.eval_expr(node.index.base)
    #node.index.count_value = self.eval_expr(node.index.count)

  def stmt_on(self, node):

    # Children
    self.expr(node.expr)
    self.stmt(node.stmt)

  def stmt_assert(self, node):
    
    # Children
    self.expr(node.expr)

  def stmt_return(self, node):
    
    # Children
    self.expr(node.expr)

  # Expressions =========================================

  # TODO: check ops only act on vars

  def expr_list(self, node):
    [self.expr(x) for x in node.children()]

  def expr_single(self, node):
     
    # Children
    self.elem(node.elem)

  def expr_unary(self, node):
    """
    Unary elements can only be value, variable or array subscript types.
    """

    # Children
    self.elem(node.elem)

  def expr_binop(self, node):
    """
    Binop (right) elements can only be singles or subscripts.
    """
     
    # Children
    self.elem(node.elem)
    self.expr(node.right)

    # Check type of right element
    if not self.check_elem_types(node.elem, [
        T_VAL_SINGLE,
        T_VAR_SINGLE, 
        T_REF_SINGLE, 
        T_VAL_SUB, 
        T_VAR_SUB, 
        T_REF_SUB]):
      self.type_error('binop right element', node.elem, node.coord)
  
  # Elements= ===========================================

  def elem_group(self, node):
    
    # Children
    self.expr(node.expr)

  def elem_id(self, node):
    
    node.symbol = self.check_decl(node.name, node.coord)

  def elem_sub(self, node):
    
    # Children
    self.expr(node.expr)

    node.symbol = self.check_decl(node.name, node.coord)

    # Check the symbol type
    if not self.sym.check_form(node.name, ['array']):
      self.type_error('array', node.name, node.coord)
    
  def elem_slice(self, node):
    
    # Children
    self.expr(node.base)
    self.expr(node.count)

    node.symbol = self.check_decl(node.name, node.coord)

    # Check the symbol type
    if not self.sym.check_form(node.name, ['array']):
      self.type_error('array', node.name, node.coord)
    
  def elem_index_range(self, node):
    
    # Children
    self.expr(node.base)
    self.expr(node.count)
    
    node.symbol = self.check_decl(node.name, node.coord)

    # Check the symbol type
    if not self.sym.check_type(node.name, [T_VAR_SINGLE]):
      self.type_error('index range variable', node.name, node.coord)

  def elem_fcall(self, node):

    # Children
    [self.expr(x) for x in node.args]
    
    node.symbol = self.check_decl(node.name, node.coord)
    self.check_def(node)

    # Mark the procedure as used in the signature table
    self.sig.mark(node.name)

  def elem_number(self, node):
    pass

  def elem_boolean(self, node):
    pass

  def elem_string(self, node):
    pass

  def elem_char(self, node):
    pass

