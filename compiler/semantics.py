# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import sys

import error
import util
import definitions as defs

import ast
from ast import NodeVisitor
import symbol
import signature
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

class Semantics(NodeVisitor):
    """ An AST visitor class to check the semantics of a sire program
    """
    def __init__(self, error):
        self.depth = 0
        self.error = error
        self.sym = symbol.SymbolTable(self, debug=False)
        self.sig = signature.SignatureTable(self, debug=False)
        self.proc_names = []
        self.init_system()

    def init_system(self):
        """ Initialise variables in the 'system' scope
        """
        # Add system variables core, chan
        self.sym.begin_scope('system')
        self.sym.insert(defs.SYS_CORE_ARRAY, Type('core', 'array'))
        self.sym.insert(defs.SYS_NUM_CORES_CONST, Type('val', 'single'))

        # Add all mobile builtin functions
        for x in builtins.values():
            self.sym.insert(x.definition.name, x.definition.type)
            self.sig.insert(x.definition.type, x.definition)
            if x.mobile:
                self.proc_names.append(x.definition.name)

    def down(self, tag):
        """ Begin a new scope """
        if tag: self.sym.begin_scope(tag)

    def up(self, tag):
        """ End the current scope """
        if tag: self.sym.end_scope()

    def get_elem_type(self, elem):
        """ Given an element, return its type """
        
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
        """ Given an expression work out its type """
        
        #If it's a single value, lookup the type
        if isinstance(expr, ast.ExprSingle):
            return self.get_elem_type(expr.elem)    
        
        # Otherwise it must be a unary or binop, and hence a var
        return Type('var', 'single')

    def check_elem_types(self, elem, types):
        """ Given an elem and a set of types, check if one matches """
        t = self.get_elem_type(elem)
        return True if t and any([x==t for x in types]) else False

    # Errors and warnings =================================

    def nodecl_error(self, name, specifier, coord):
        """ No declaration error
        """
        self.error.report_error("{} '{}' not declared"
                .format(specifier, name), coord)

    def badargs_error(self, name, coord):
        """ No definition error 
        """
        self.error.report_error("invalid arguments for procedure '{}' "
                .format(name), coord)

    def redecl_error(self, name, coord):
        """ Re-declaration error 
        """
        self.error.report_error("variable '{}' already declared in scope"
                .format(name), coord)

    def redef_error(self, name, coord):
        """ Re-definition error 
        """
        self.error.report_error("procedure '{}' already declared"
                .format(name), coord)

    def procedure_def_error(self, name, coord):
        """ Re-definition error 
        """
        self.error.report_error("procedure '{}' definition invalid"
                .format(name), coord)

    def unused_warning(self, name, coord):
        """ Unused variable warning
        """
        self.error.report_warning("variable '{}' declared but not used"
                .format(name), coord)

    def type_error(self, msg, name, coord):
        """ Mismatching type error
        """
        self.error.report_error("type error in {} with '{}'".format(msg, name), coord)

    def form_error(self, msg, name, coord):
        """ Mismatching form error
        """
        self.error.report_error("form error in {} with '{}'"
                .format(msg, name), coord)

    # Program ============================================

    def visit_program(self, node):
        return 'program'
    
    # Variable declarations ===============================

    def visit_decls(self, node):
        pass

    def visit_decl(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    # Procedure definitions ===============================

    def visit_defs(self, node):
        pass

    def visit_def(self, node):
        # Rename main to avoid conflicts in linking
        if node.name == 'main':
            node.name = '_'+node.name
        if self.sym.insert(node.name, node.type, node.coord):
            if not self.sig.insert(node.type, node):
                self.procedure_def_error(node.name, node.coord)
        else:
            self.redecl_error(node.name, node.coord)
        self.proc_names.append(node.name)
        self.parent = node.name
        return 'proc'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

        # TODO: For alias parameters, check expr is composed of param values
        if node.type.form == 'alias':
            pass
            #if not self.get_expr_type(node.expr).form == 'alias'

    # Statements ==========================================

    def visit_stmt_seq(self, node):
        pass

    def visit_stmt_par(self, node):
        pass

    def visit_stmt_skip(self, node):
        pass

    def visit_stmt_pcall(self, node):
        
        # Check the name is declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'process', node.coord)
        
        else:
            # Check the arguments are correct
            if not self.sig.check_args('proc', node):
                self.badargs_error(node.name, node.coord)
            
            # And mark the symbol as used
            self.sym.mark_decl(node.name)

    def visit_stmt_ass(self, node):
        if not self.check_elem_types(node.left, [
               Type('val', 'single'), 
               Type('var', 'single'), 
               Type('val', 'sub'),
               Type('var', 'sub')]):
            self.type_error('assignment', node.left.name, node.coord)

    def visit_stmt_aliases(self, node):
        if not self.sym.check_form(node.dest, ['alias']):
            self.type_error('alias', node.dest, node.coord)
        if not self.sym.check_form(node.name, ['var', 'alias', 'array']):
            self.type_error('alias', node.name, node.coord)

    def visit_stmt_if(self, node):
        pass

    def visit_stmt_while(self, node):
        pass

    def visit_stmt_for(self, node):
        if not self.check_elem_types(node.var, [Type('var', 'single')]):
            self.type_error('for loop index variable', node.var.name, node.coord)

    def visit_stmt_par(self, node):
        if not self.check_elem_types(node.var, [Type('var', 'single')]):
            self.type_error('repliacator index variable', node.var.name, node.coord)

    def visit_stmt_on(self, node):
        if not self.check_elem_types(node.core, [Type('core', 'sub')]):
            self.type_error('on target', node.core, node.coord)

    def visit_stmt_return(self, node):
        pass

    # Expressions =========================================

    # TODO: check ops only act on vars

    def visit_expr_list(self, node):
        pass

    def visit_expr_single(self, node):
        #if not self.check_elem_types(node.elem, 
        #        [Type('var', 'single'), Type('var', 'sub')]):
        #    self.type_error('single', node.elem, node.coord)
        pass

    def visit_expr_unary(self, node):
        if not self.check_elem_types(node.elem,
                [Type('var', 'single'), Type('var', 'sub'), 
                    Type('val', 'single')]):
            self.type_error('unary', node.elem, node.coord)

    def visit_expr_binop(self, node):
        if not self.check_elem_types(node.elem, [
                Type('val', 'single'),
                Type('var', 'single'), 
                Type('var', 'array'), 
                Type('val', 'sub'), 
                Type('var', 'sub')]):
            self.type_error('binop dest', node.elem, node.coord)
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        pass

    def visit_elem_id(self, node):
        # Check the symbol has been declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'variable', node.coord)
        # Mark it as used if it has and link to the symbol
        else:
            node.symbol = self.sym.lookup(node.name)
            self.sym.mark_decl(node.name)
        # Check it has the right form
        #if not self.sym.check_form(node.name, ['single']):
        #    self.form_error('single', node.name, node.coord)

    def visit_elem_sub(self, node):
        # Check the symbol has been declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'array or alias', node.coord)
        # Mark it as used if it has and link to the symbol
        else:
            node.symbol = self.sym.lookup(node.name)
            self.sym.mark_decl(node.name)
        # Check it has the right form 
        #if not self.sym.check_form(node.name, ['array','alias']):
        #    self.form_error('subscript', node.name, node.coord)

    def visit_elem_slice(self, node):
        # Check the symbol has been declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'array or alias', node.coord)
        # Mark it as used if it has and link to the symbol
        else:
            node.symbol = self.sym.lookup(node.name)
            self.sym.mark_decl(node.name)

    def visit_elem_pcall(self, node):
        # Check the name is declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'process', node.coord)
        else:
            # Check the arguments are correct
            if not self.sig.check_args('proc', node):
                self.badargs_error(node.name, node.coord)
            # And mark the symbol as used
            self.sym.mark_decl(node.name)

    def visit_elem_fcall(self, node):
        # Check the name is declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'function', node.coord)
        else:
            # Check the arguments are correct
            if not self.sig.check_args('func', node):
                self.badargs_error(node.name, node.coord)
            # And mark the symbol as used
            self.sym.mark_decl(node.name)

    def visit_elem_number(self, node):
        pass

    def visit_elem_boolean(self, node):
        pass

    def visit_elem_string(self, node):
        pass

    def visit_elem_char(self, node):
        pass

