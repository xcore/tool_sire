import sys
import error
import ast
import symbol
import signature

# Declarations:
types = ['var', 'val', 'chanend', 'chan', 'port', 'core']
form  = ['single', 'array', 'alias', 'sub']

elem_types = {
    'fcall'   : 'var',
    'number'  : 'var',
    'boolean' : 'var',
    'char'    : 'var',
    'string'  : 'array'
}

SYS_CORE_ARRAY = 'core'
SYS_CHAN_ARRAY = 'chan'

class Semantics(ast.NodeVisitor):
    """ An AST visitor class to check the semantics of a sire program
    """
    def __init__(self, error):
        self.depth = 0
        self.error = error
        self.sym = symbol.SymbolTable(self)
        self.sig = signature.SignatureTable(self)

        # Add system variables core, chan
        self.sym.begin_scope('system')
        self.sym.insert(SYS_CORE_ARRAY, 'core', None)
        self.sym.insert(SYS_CHAN_ARRAY, 'chanend', None)

    def down(self, tag):
        """ Begin a new scope """
        if tag: self.sym.begin_scope(tag)

    def up(self, tag):
        """ End the current scope """
        if tag: self.sym.end_scope()

    def get_type(self, expr):
        """ Given an expression work out its type """
        if isinstance(expr, ast.ExprSingle):
            # If its an ID or subscript, look it up
            if isinstance(expr.elem, ast.Id) or isinstance(expr.elem, ast.Sub):
                return self.sym.lookup(expr.elem.name).type
            # We know otherwise for each element
            else:
                return elem_types[expr.elem.__class__.__name__]
        # Otherwise it must be a unary or binop, and hence a var
        else:
            return 'var'

    # Errors and warnings =================================

    def nodecl_error(self, name, coord):
        """ No declaration error """
        self.error.report_error("variable '{}' not declared"
                .format(name, coord))

    def nodef_error(self, name, coord):
        """ No definition error """
        self.error.report_error("procedure '{}' not defined"
                .format(name, coord))

    def redecl_error(self, name, coord):
        """ Re-declaration error """
        self.error.report_error("variable '{}' already declared in scope"
                .format(name, coord))

    def redef_error(self, name, coord):
        """ Re-definition error """
        self.error.report_error("procedure '{}' already declared"
                .format(name, coord))

    def unused_warning(self, name, coord):
        """ Unused variable warning """
        error.report_error("variable '{}' declared but not used"
                .format(name, coord))

    # Program ============================================

    def visit_program(self, node):
        return 'program'
    
    # Variable declarations ===============================

    def visit_decls(self, node):
        pass

    def visit_decl_single(self, node):
        if not self.sym.insert(node.type, node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_array(self, node):
        if not self.sym.insert(node.type, node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_val(self, node):
        if not self.sym.insert('val', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_decl_port(self, node):
        if not self.sym.insert('port', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    # Procedure declarations ==============================

    def visit_defs(self, node):
        pass

    def visit_def_proc(self, node):
        if not self.sig.insert('proc', node):
            self.redef_error(node.name, node.coord)
        return 'proc'
    
    def visit_def_func(self, node):
        if not self.sig.insert('func', node):
            self.redef_error(node.name, node.coord)
        return 'func'
    
    # Formals =============================================
    
    def visit_formals(self, node):
        pass

    def visit_param_var(self, node):
        if not self.sym.insert('var', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_alias(self, node):
        if not self.sym.insert('alias', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_val(self, node):
        if not self.sym.insert('val', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    def visit_param_chanend(self, node):
        if not self.sym.insert('chanend', node.name, node.coord):
            self.redecl_error(node.name, node.coord)

    # Statements ==========================================

    def visit_stmt_seq(self, node):
        pass

    def visit_stmt_par(self, node):
        pass

    def visit_stmt_skip(self, node):
        pass

    def visit_stmt_pcall(self, node):
        if not self.sig.check_def('proc', node):
            self.nodef_error(node.name, node.coord)

    def visit_stmt_ass(self, node):
        if not self.sym.check_type(node.left, ('var')):
            self.type_error('assignment', node.left, node.coord)

    def visit_stmt_in(self, node):
        if not self.sym.check_type(node.left, ('chanend', 'port')):
            self.type_error('input', node.left, node.coord)

    def visit_stmt_out(self, node):
        if not self.sym.check_type(node.left, ('chanend', 'port')):
            self.type_error('output', node.left, node.coord)

    def visit_stmt_if(self, node):
        pass

    def visit_stmt_while(self, node):
        pass

    def visit_stmt_for(self, node):
        pass

    def visit_stmt_on(self, node):
        if not self.sym.check_type(node.core, ('core')):
            self.type_error('on target', node.core, node.coord)
        if not self.sig.check_def('proc', node.pcall):
            self.undef_error(node.name, node.coord)

    def visit_stmt_connect(self, node):
        if not self.sym.check_type(node.core, ('core')):
            self.type_error('connect target', node.core, node.coord)

    def visit_stmt_aliases(self, node):
        self.sym.check_type(node.name, ('alias'))

    def visit_stmt_return(self, node):
        pass

    # Expressions =========================================

    # TODO: check ops only act on vars

    def visit_expr_list(self, node):
        pass

    def visit_expr_single(self, node):
        if not self.sym.check_type(node.right, ('var')):
            self.type_error('single', node.left, node.coord)

    def visit_expr_unary(self, node):
        if not self.sym.check_type(node.left, ('var')):
            self.type_error('unary', node.left, node.coord)

    def visit_expr_binop(self, node):
        if not self.sym.check_type(node.elem, ('var')):
            self.type_error('binop dest', node.left, node.coord)
    
    # Elements= ===========================================

    def visit_elem_group(self, node):
        pass

    def visit_elem_sub(self, node):
        if not self.sym.check_decl(node.name, ('array','alias')):
            self.decl_error(node.name)
        self.sym.mark_decl(node.name)

    def visit_elem_fcall(self, node):
        self.sig.check_def('func', node.name)

    def visit_elem_number(self, node):
        pass

    def visit_elem_boolean(self, node):
        pass

    def visit_elem_string(self, node):
        pass

    def visit_elem_char(self, node):
        pass

    def visit_elem_id(self, node):
        if not self.sym.check_decl(node.value, ('single')):
            self.decl_error(node.value)
        self.sym.mark_decl(node.name)

