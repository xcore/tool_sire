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
    Type('var', 'sub')    : Type('val', 'single'),
    Type('ref', 'sub')    : Type('val', 'single'),
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
        
        # If its an expression group, get_expr_type
        if isinstance(elem, ast.ElemGroup):
            return self.get_expr_type(elem.expr)
        
        # If its a single identifer, look it up (if it exists)
        elif isinstance(elem, ast.ElemId):
            s = self.sym.lookup(elem.name)
            if s: 
                return s.type
            else:
                self.nodecl_error(elem.name, 'single', None)
                return None
        
        # If its a subscripted identifier, lookup and return subscripted type
        elif isinstance(elem, ast.ElemSub):
            s = self.sym.lookup(elem.name)
            if s:
                return s.type.subscriptOf()
            else:
                self.nodecl_error(elem.name, 'array', None)
                return None

        # If it is an array slice
        elif isinstance(elem, ast.ElemSlice):
            s = self.sym.lookup(elem.name)
            if s:
                return s.type
            else:
                self.nodecl_error(elem.name, 'array', None)
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

    def check_args(self, type, node):
        """ 
        Check if a procedure signature is defined for a [pf]call AST node.
        """
      
        # Compare each param type to the type of each expr argument
        if self.debug:
           print('Checking args for {}'.format(node.name))
        
        # Check the signature exists.
        if not self.sig.sig_exists(node.name):
            return False

        # Check there is the right number
        if len(self.sig.get_params(node.name)) != len(node.args):
            return False
        
        # Check the type of each actual matches the formal
        for (x, y) in zip(self.sig.get_params(node.name), node.args):
            t = self.get_expr_type(y)
            if self.debug:
                print('Arg type: {}'.format(t))
                print('Param type: {}'.format(x.type))

            # If argument y has no type, i.e. not defined
            if not t:
                return False

            # Check it against each valid conversion
            if not any(t==z for z in param_conversions[x.type]):
                return False
        
        return True
   
    # Errors and warnings =================================

    def nodecl_error(self, name, specifier, coord):
        """ 
        No declaration error
        """
        self.errorlog.report_error(
                "{} '{}' not declared"
                .format(specifier, name), coord)

    def badargs_error(self, name, coord):
        """ 
        No definition error 
        """
        self.errorlog.report_error(
                "invalid arguments for procedure '{}' "
                .format(name), coord)

    def redecl_error(self, name, coord):
        """
        Re-declaration error 
        """
        self.errorlog.report_error(
                "variable '{}' already declared in scope"
                .format(name), coord)

    def redef_error(self, name, coord):
        """ 
        Re-definition error 
        """
        self.errorlog.report_error(
                "procedure '{}' already declared"
                .format(name), coord)

    def procedure_def_error(self, name, coord):
        """ 
        Re-definition error 
        """
        self.errorlog.report_error(
                "procedure '{}' definition invalid"
                .format(name), coord)

    def type_error(self, msg, name, coord):
        """ 
        Mismatching type error
        """
        self.errorlog.report_error(
                "type error in {} with '{}'"
                .format(msg, name), coord)

    def form_error(self, msg, name, coord):
        """ 
        Mismatching form error
        """
        self.errorlog.report_error(
                "form error in {} with '{}'"
                .format(msg, name), coord)

    # Program ============================================

    def walk_program(self, node):
        self.sym.begin_scope('program')
        [self.decl(x) for x in node.decls]
        [self.defn(x) for x in node.defs]
        #self.sym.end_scope()
    
    # Variable declarations ===============================

    def decl(self, node):
        if not self.sym.lookup_scoped(node.name):
            self.sym.insert(node.name, node.type, node.expr, node.coord)
            node.symbol = self.sym.lookup(node.name)
        else:
            self.redecl_error(node.name, node.coord)

        # Children
        if node.expr:
            self.expr(node.expr)

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
            self.sym.insert(node.name, node.type, node.expr, node.coord)
            node.symbol = self.sym.lookup(node.name)
        else:
            self.redecl_error(node.name, node.coord)

        # TODO: For array reference parameters, check length expr is composed of
        # param values

        # Children
        if node.type == Type('ref', 'array'):
            self.expr(node.expr)

    # Statements ==========================================

    def stmt_seq(self, node):
        [self.stmt(x) for x in node.children()]

    def stmt_par(self, node):
        [self.stmt(x) for x in node.children()]

    def stmt_skip(self, node):
        pass

    def stmt_pcall(self, node):
        
        # Check the name is declared
        if self.sym.check_decl(node.name):
            # Check the arguments are correct
            if not self.check_args('proc', node):
                self.badargs_error(node.name, node.coord)
            # And mark the symbol as used
            s = self.sym.lookup(node.name)
            s.mark_used()
        else:
            self.nodecl_error(node.name, 'process', node.coord)

        # TODO: check actual-formal types match, e.g. with refs.

        # Children
        [self.expr(x) for x in node.args]

    def stmt_ass(self, node):

        # Check valid type for assignment target
        if not self.check_elem_types(node.left, [
               Type('val', 'single'), 
               Type('var', 'single'), 
               Type('ref', 'single'), 
               Type('var', 'sub'),
               Type('ref', 'sub'),]):
            self.type_error('assignment', node.left.name, node.coord)

        # Children
        self.elem(node.left)
        self.expr(node.expr)

    def stmt_alias(self, node):

        if self.sym.check_form(node.name, ['array']):
            node.symbol = self.sym.lookup(node.name)
            self.sym.mark_used(node.name)
        else:
            self.type_error('array', node.dest, node.coord)
        
        if not self.sym.check_form(node.slice.name, ['array']):
            self.type_error('array', node.slice.name, node.coord)

        # Children
        self.expr(node.slice)

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
        
        if not self.check_elem_types(node.var, [Type('var', 'single')]):
            self.type_error('for loop index variable', node.var.name, node.coord)

        # Children
        self.elem(node.var)
        self.expr(node.init)
        self.expr(node.bound)
        self.expr(node.step)
        self.stmt(node.stmt)

    def stmt_rep(self, node):
        
        if not self.check_elem_types(node.var, [Type('var', 'single')]):
            self.type_error('repliacator index variable', node.var.name, node.coord)
        
        # Children
        self.elem(node.var)
        self.expr(node.init)
        self.expr(node.count)
        self.elem(node.stmt)

    def stmt_on(self, node):
        if not self.check_elem_types(node.core, [Type('core', 'sub')]):
            self.type_error('on target', node.core, node.coord)

        # Children
        self.elem(node.pcall)

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
        #if not self.check_elem_types(node.elem, [
        #        Type('val', 'single'),
        #        Type('var', 'single'), 
        #        Type('var', 'sub')]):
        #    self.type_error('unary', node.elem, node.coord)

        # Children
        self.elem(node.elem)

    def expr_binop(self, node):
        """
        Binop (right) elements can only be singles or subscripts.
        """
        if not self.check_elem_types(node.elem, [
                Type('val', 'single'),
                Type('var', 'single'), 
                Type('ref', 'single'), 
                Type('val', 'sub'), 
                Type('var', 'sub'), 
                Type('ref', 'sub')]):
            self.type_error('binop right element', node.elem, node.coord)
       
        # Children
        self.elem(node.elem)
        self.expr(node.right)
    
    # Elements= ===========================================

    def elem_group(self, node):
        
        # Children
        self.expr(node.expr)

    def elem_id(self, node):
        
        # Check the symbol has been declared
        if self.sym.check_decl(node.name):
            node.symbol = self.sym.lookup(node.name)
            node.symbol.mark_used()
        else:
            self.nodecl_error(node.name, 'variable', node.coord)

    def elem_sub(self, node):
        
        # Check the symbol has been declared
        if self.sym.check_decl(node.name):
            node.symbol = self.sym.lookup(node.name)
            node.symbol.mark_used()
        else:
            self.nodecl_error(node.name, 'array subscript', node.coord)
        
        # Children
        self.expr(node.expr)

    def elem_slice(self, node):
        
        # Check the symbol has been declared
        if self.sym.check_decl(node.name):
            node.symbol = self.sym.lookup(node.name)
            node.symbol.mark_used()
        else:
            self.nodecl_error(node.name, 'array slice', node.coord)
        
        # Children
        self.expr(node.begin)
        self.expr(node.end)

    def elem_pcall(self, node):
        
        # Check the name is declared
        s = self.sym.check_decl(node.name)
        if s:
            # Check the arguments are correct
            if not self.check_args('proc', node):
                self.badargs_error(node.name, node.coord)
            # And mark the symbol as used
            s.mark_used()
        else:
            self.nodecl_error(node.name, 'process', node.coord)
        
        # Children
        [self.expr(x) for x in node.args]

    def elem_fcall(self, node):
        
        # Check the name is declared
        if self.sym.check_decl(node.name):
            # Check the arguments are correct
            if not self.check_args('func', node):
                self.badargs_error(node.name, node.coord)
            # And mark the symbol as used
            s = self.sym.lookup(node.name)
            s.mark_used()
        else:
            self.nodecl_error(node.name, 'function', node.coord)

        # Children
        [self.expr(x) for x in node.args]

    def elem_number(self, node):
        pass

    def elem_boolean(self, node):
        pass

    def elem_string(self, node):
        pass

    def elem_char(self, node):
        pass

