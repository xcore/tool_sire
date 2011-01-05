import sys
import error
import util
import ast
import symbol
import signature
from type import Type

SYS_CORE_ARRAY = 'core'
SYS_CHAN_ARRAY = 'chan'

elem_types = {
    'elem_sub'     : None,
    'elem_id'      : None,
    'elem_group'   : None,
    'elem_fcall'   : Type('var', 'single'),
    'elem_number'  : Type('var', 'single'),
    'elem_boolean' : Type('var', 'single'),
    'elem_string'  : Type('var', 'array'),
    'elem_char'    : Type('var', 'single'),
}

class Semantics(ast.NodeVisitor):
    """ An AST visitor class to check the semantics of a sire program
    """
    def __init__(self, error):
        self.depth = 0
        self.error = error
        self.sym = symbol.SymbolTable(self, debug=False)
        self.sig = signature.SignatureTable(self)

        # Add system variables core, chan
        self.sym.begin_scope('system')
        self.sym.insert(SYS_CORE_ARRAY, Type('core', 'array'), None)
        self.sym.insert(SYS_CHAN_ARRAY, Type('chanend', 'array'), None)

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
        # If its an identifer, look it up (if it exists)
        elif isinstance(elem, ast.ElemId) or isinstance(elem, ast.ElemSub):
            if self.sym.check_decl(elem.name):
                return self.sym.lookup(elem.name).type
            else:
                self.nodecl_error(elem.name, 'variable or array', None)
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
        for x in types:
            if x == t: return True
        return False

    # Errors and warnings =================================

    def nodecl_error(self, name, specifier, coord):
        """ No declaration error """
        self.error.report_error("{} '{}' not declared"
                .format(specifier, name), coord)

    def badargs_error(self, name, coord):
        """ No definition error """
        self.error.report_error("invalid argumens for procedure '{}' "
                .format(name), coord)

    def redecl_error(self, name, coord):
        """ Re-declaration error """
        self.error.report_error("variable '{}' already declared in scope"
                .format(name), coord)

    def redef_error(self, name, coord):
        """ Re-definition error """
        self.error.report_error("procedure '{}' already declared"
                .format(name), coord)

    def unused_warning(self, name, coord):
        """ Unused variable warning """
        self.error.report_warning("variable '{}' declared but not used"
                .format(name), coord)

    def type_error(self, msg, name, coord):
        """ Mismatching type error """
        self.error.report_error("type error in {} with '{}'".format(msg, name), coord)

    def form_error(self, msg, name, coord):
        """ Mismatching form error """
        self.error.report_error("form error in {} with '{}'"
                .format(msg, name), coord)

    # Program ============================================

    def visit_program(self, node):
        return 'program'
    
    # Variable declarations ===============================

    def visit_decls(self, node):
        pass

    def visit_decl_single(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_array(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_val(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_port(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    # Procedure definitions ===============================

    def visit_defs(self, node):
        pass

    def visit_def_proc(self, node):
        if self.sym.insert(node.name, node.type, node.coord):
            self.sig.insert('proc', node)
        else:
            self.redecl_error(node.name, node.coord)
        return 'proc'
    
    def visit_def_func(self, node):
        if self.sym.insert(node.name, node.type, node.coord):
            self.sig.insert('func', node)
        else:
            self.redecl_error(node.name, node.coord)
        return 'func'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param_single(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_alias(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_val(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_chanend(self, node):
        if not self.sym.insert(node.name, node.type, node.coord):
            self.redecl_error(node.name, node.coord)

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
        if not self.check_elem_types(node.left, 
                [Type('var', 'single'), Type('var', 'array'), 
                    Type('var', 'alias')]):
            self.type_error('assignment', node.left.name, node.coord)

    def visit_stmt_in(self, node):
        if not self.check_elem_types(node.left, 
                [Type('chanend', 'single'), Type('port', 'single')]):
            self.type_error('input', node.left.name, node.coord)

    def visit_stmt_out(self, node):
        if not self.check_elem_types(node.left, 
                [Type('chanend', 'single'), Type('port', 'single')]):
            self.type_error('output', node.left.name, node.coord)

    def visit_stmt_if(self, node):
        pass

    def visit_stmt_while(self, node):
        pass

    def visit_stmt_for(self, node):
        pass

    def visit_stmt_on(self, node):
        if not self.check_elem_types(node.core, [Type('core', 'array')]):
            self.type_error('on target', node.core, node.coord)

    def visit_stmt_connect(self, node):
        if not self.check_elem_types(node.core, [Type('core', 'sub')]):
            self.type_error('connect target', node.core, node.coord)

    def visit_stmt_aliases(self, node):
        if not self.check_elem_types(node.left, [Type('var', 'alias')]):
            self.type_error('alias', node.left, node.coord)
        if not self.check_elem_types(node.name, 
                [Type('var', 'array'), Type('var', 'alias')]):
            self.type_error('alias', node.name, node.coord)

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
        if not self.check_elem_types(node.elem, 
                [Type('var', 'single'), Type('var', 'array'), 
                    Type('var', 'alias'), Type('val', 'single')]):
            self.type_error('binop dest', node.elem, node.coord)
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        pass

    def visit_elem_id(self, node):
        # Check the symbol has been declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'variable', node.coord)
        # Mark it as used if it has
        else:
            self.sym.mark_decl(node.name)
        # Check it has the right form
        #if not self.sym.check_form(node.name, ['single']):
        #    self.form_error('single', node.name, node.coord)

    def visit_elem_sub(self, node):
        # Check the symbol has been declared
        if not self.sym.check_decl(node.name):
            self.nodecl_error(node.name, 'array', node.coord)
        # Mark it as used if it has
        else:
            self.sym.mark_decl(node.name)
        # Check it has the right form 
        #if not self.sym.check_form(node.name, ['array','alias']):
        #    self.form_error('subscript', node.name, node.coord)

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

