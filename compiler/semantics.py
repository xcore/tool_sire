# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import error
import util
import definitions as defs

import ast
from walker import NodeWalker
from builtin import builtins
from type import Type
from evalexpr import EvaluateExpr

elem_types = {
  'elem_sub'     : None,
  'elem_id'      : None,
  'elem_group'   : None,
  'elem_fcall'   : Type('var', 'single'),
  'elem_string'  : Type('var', 'array'),
  'elem_number'  : Type('val', 'single'),
  'elem_boolean' : Type('val', 'single'),
  'elem_char'    : Type('val', 'single'),
  }

# Valid actual parameter types that can be taken by each formal type.
param_conversions = {
  
  Type('val', 'single') : [
    Type('val', 'single'), 
    Type('var', 'single'), 
    Type('ref', 'single'), 
    Type('var', 'sub'),
    Type('ref', 'sub'),
  ],

  Type('ref', 'single') : [
    Type('var', 'single'), 
    Type('ref', 'single'), 
    Type('var', 'sub'),
    Type('ref', 'sub'),
  ],

  Type('ref', 'array') : [
    Type('var', 'array'), 
    Type('ref', 'array'), 
  ],
}

# Relation of variable types to formal parameter types for parallel composition.
par_var_to_param = {
  Type('val', 'single') : Type('val', 'single'),
  Type('var', 'single') : Type('ref', 'single'), 
  Type('ref', 'single') : Type('ref', 'single'),
  Type('var', 'sub')    : Type('val', 'single'),
  Type('ref', 'sub')    : Type('val', 'single'),
  Type('var', 'array')  : Type('ref', 'array'), 
  Type('ref', 'array')  : Type('ref', 'array'),
}

# Relation of variable types to formal parameter types for parallel replication.
# All singles map to values as there can be no single assignment in a
# replicator.
rep_var_to_param = {
  Type('val', 'single') : Type('val', 'single'),
  Type('var', 'single') : Type('val', 'single'), 
  Type('ref', 'single') : Type('val', 'single'),
  Type('var', 'sub')  : Type('val', 'single'),
  Type('ref', 'sub')  : Type('val', 'single'),
  Type('var', 'array')  : Type('ref', 'array'), 
  Type('ref', 'array')  : Type('ref', 'array'),
}

class Semantics(NodeWalker):
  """ 
  An AST walker class to check the semantics of a sire program.
  """
  def __init__(self, sym, sig, errorlog, debug=False):
    self.sym = sym
    self.sig = sig
    self.errorlog = errorlog
    self.debug = debug
    
    # Initialise variables in the 'system' scope
    
    # Add system variables core, chan
    self.sym.begin_scope('system')
    self.sym.insert(defs.SYS_CORE_ARRAY, Type('core', 'array'))
    self.sym.insert(defs.SYS_NUM_CORES_CONST, Type('val', 'single'))

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
    return Type('var', 'single')

  def check_elem_types(self, elem, types):
    """ 
    Given an elem and a set of types, check if one matches
    """
    t = self.get_elem_type(elem)
    return True if t and any([x==t for x in types]) else False

  def check_def(self, node):
    """ 
    Check if a procedure signature is defined for a [pf]call AST node.
    """
    
    # Compare each param type to the type of each expr argument
    if self.debug:
       print('Checking args for {}'.format(node.name))
    
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
      if self.debug:
        print('Arg type: {}'.format(t))
        print('Param type: {}'.format(x.type))

      # If argument y has no type, i.e. not defined
      if not t:
        self.nodef_error(node.name, node.coord)
        return False

      # Check it against each valid conversion
      if not any(t==z for z in param_conversions[x.type]):
        self.nodef_error(node.name, node.coord)
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
    v = EvaluateExpr().expr(expr)
    if v == None:
      self.non_const_error()
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
    Re-definition
    """
    self.errorlog.report_error(
        "procedure '{}' definition invalid"
        .format(name), coord)

  def type_error(self, msg, name, coord):
    """ 
    Mismatching type
    """
    self.errorlog.report_error(
        "type error in {} with '{}'"
        .format(msg, name), coord)

  def form_error(self, msg, name, coord):
    """ 
    Mismatching form
    """
    self.errorlog.report_error(
        "form error in {} with '{}'"
        .format(msg, name), coord)

  def non_const_error(self):
    """
    Constant expression cannot be evaluated
    """
    self.errorlog.report_error("non-constant in expr")
    
  def array_param_bound_decl_error(self, name, coord):
    """ 
    Array parameter length declaration is not constant or referenced by a
    single variable parameter.
    """
    self.errorlog.report_error(
        "invalid array length for '{}'"
        .format(name), coord)

  # Program ============================================

  def walk_program(self, node):
    self.sym.begin_scope('program')
    [self.decl(x) for x in node.decls]
    [self.defn(x) for x in node.defs]
    #self.sym.end_scope()
  
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
    if (node.type == Type('val', 'single') 
        or node.type == Type('var', 'array')):
      node.symbol.value = self.eval_expr(node.expr)

  # Procedure definitions ===============================

  def defn(self, node):
    
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

    # Begin a new scope for decls and stmt components
    self.sym.begin_scope('proc')
    
    # Iterate over in parameters in reverse so length specifiers have been
    # declared, which should appear after the array reference they relate to.
    [self.param(x) for x in reversed(node.formals)]
     
    # Check if this is a prototype or the actual definition
    if node.stmt:
      
      # If there was a prototype, unmark it
      s.unmark_prototype()

      # Add the procedure name to the list
      self.parent = node.name
    
      # Declarations
      [self.decl(x) for x in node.decls]

      # Body statement
      self.stmt(node.stmt)
    
    # End the scope
    self.sym.end_scope(warn_unused=True if node.stmt else False)
      
  
  # Formals =============================================
  
  def param(self, node):
     
    if not self.sym.lookup_scoped(node.name):
      s = self.sym.insert(node.name, node.type, node.expr, node.coord)
      node.symbol = s
    else:
      self.redecl_error(node.name, node.coord)

    # Try and determine the array bound (if it's constant valued)
    if node.type == Type('ref', 'array'):
      node.symbol.value = EvaluateExpr().expr(node.expr)
      #print(node.name+' = {}'.format(node.symbol.value))

      # If it's not constant-valued, then check it's a single variable.
      if (node.symbol.value == None
          and not isinstance(node.expr, ast.ExprSingle)):
        self.array_param_bound_decl_error(node.name, node.coord)

    # Children
    if node.type == Type('ref', 'array'):
      self.expr(node.expr)

  # Statements ==========================================

  def stmt_seq(self, node):
    [self.stmt(x) for x in node.stmt]

  def stmt_par(self, node):
    [self.stmt(x) for x in node.stmt]

  def stmt_skip(self, node):
    pass

  def stmt_pcall(self, node):

    # Children
    [self.expr(x) for x in node.args]

    # Check the decl and def
    node.symbol = self.check_decl(node.name, node.coord)
    self.check_def(node)
    
    # TODO: check actual-formal types match, e.g. with refs.

  def stmt_ass(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for assignment target
    if not self.check_elem_types(node.left, [
         Type('val', 'single'), 
         Type('var', 'single'), 
         Type('ref', 'single'), 
         Type('var', 'sub'),
         Type('ref', 'sub'),]):
      self.type_error('assignment', node.left.name, node.coord)

  def stmt_in(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for assignment target
    if not self.check_elem_types(node.left, [
         Type('chan',  'single'), 
         Type('chanend', 'single'), 
         Type('chan',  'sub'),
         Type('chanend', 'sub'),]):
      self.type_error('input', node.left.name, node.coord)

  def stmt_out(self, node):

    # Children
    self.elem(node.left)
    self.expr(node.expr)

    # Check valid type for assignment target
    if not self.check_elem_types(node.left, [
         Type('chan',  'single'), 
         Type('chanend', 'single'), 
         Type('chan',  'sub'),
         Type('chanend', 'sub'),]):
      self.type_error('input', node.left.name, node.coord)

  def stmt_alias(self, node):

    # Children
    self.expr(node.slice)
    
    node.symbol = self.check_decl(node.name, node.coord)

    # Check the target variable type
    if not self.sym.check_form(node.name, ['array']):
      self.type_error('array', node.dest, node.coord)
    
    # Check the element is a slice
    if not isinstance(node.slice, ast.ElemSlice):
      self.slice_error('alias', node.coord)

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
      self.index_range_error('for loop', node.coord)

  def stmt_rep(self, node):
    
    # Children
    [self.elem(x) for x in node.indicies]
    self.elem(node.stmt)
    
    # Check all index elements are ElemIndexRanges
    for x in node.indicies:
      if not isinstance(x, ast.ElemIndexRange):
        self.index_range_error('parallel replicator', node.coord)

  def stmt_on(self, node):

    # Children
    self.elem(node.core)
    self.stmt(node.stmt)

    # Check the type of the core element
    if not self.check_elem_types(node.core, [Type('core', 'sub')]):
      self.type_error('on target', node.core, node.coord)

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
        Type('val', 'single'),
        Type('var', 'single'), 
        Type('ref', 'single'), 
        Type('val', 'sub'), 
        Type('var', 'sub'), 
        Type('ref', 'sub')]):
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
    if not self.sym.check_type(node.name, [Type('var', 'single')]):
      self.type_error('index range variable', node.name, node.coord)
      
    # Determine the values of the base and count expressions  
    node.base_value = self.eval_expr(node.base)
    node.count_value = self.eval_expr(node.count)

  def elem_fcall(self, node):

    # Children
    [self.expr(x) for x in node.args]
    
    node.symbol = self.check_decl(node.name, node.coord)
    self.check_def(node)

  def elem_number(self, node):
    pass

  def elem_boolean(self, node):
    pass

  def elem_string(self, node):
    pass

  def elem_char(self, node):
    pass

