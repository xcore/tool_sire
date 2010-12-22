#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# ast.cfg 
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
#-----------------------------------------------------------------

import sys

class Node(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def accept(self, visitor):
        """ Accept a visitor
        """
        pass


class NodeVisitor(object):
    """ Generic Node visitor base class to be subclassed
    """
    pass

class Program(Node):
    def __init__(self, var_decls, proc_decls, coord=None):
        self.var_decls = var_decls
        self.proc_decls = proc_decls
        self.coord = coord

    def children(self):
        c = []
        if self.var_decls is not None: c.append(self.var_decls)
        if self.proc_decls is not None: c.append(self.proc_decls)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_program(self)
        for c in self.children():
            c.accept(visitor)


class VarDecls(Node):
    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord

    def children(self):
        c = []
        if self.decl is not None: c.extend(self.decl)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_vardecls(self)
        for c in self.children():
            c.accept(visitor)


class VarDecl(Node):
    def __init__(self, form, type, name, expr, coord=None):
        self.form = form
        self.type = type
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_vardecl(self)
        for c in self.children():
            c.accept(visitor)


class ProcDecls(Node):
    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord

    def children(self):
        c = []
        if self.decl is not None: c.extend(self.decl)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_procdecls(self)
        for c in self.children():
            c.accept(visitor)


class ProcDecl(Node):
    def __init__(self, type, name, formals, var_decls, stmt, coord=None):
        self.type = type
        self.name = name
        self.formals = formals
        self.var_decls = var_decls
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.formals is not None: c.append(self.formals)
        if self.var_decls is not None: c.append(self.var_decls)
        if self.stmt is not None: c.append(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_procdecl(self)
        for c in self.children():
            c.accept(visitor)


class Formals(Node):
    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        c = []
        if self.params is not None: c.extend(self.params)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_formals(self)
        for c in self.children():
            c.accept(visitor)


class Param(Node):
    def __init__(self, type, name, coord=None):
        self.type = type
        self.name = name
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_param(self)
        for c in self.children():
            c.accept(visitor)


class Skip(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def accept(self, visitor):
        visitor.visit_skip(self)
        for c in self.children():
            c.accept(visitor)


class Pcall(Node):
    def __init__(self, name, expr, coord=None):
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_pcall(self)
        for c in self.children():
            c.accept(visitor)


class Ass(Node):
    def __init__(self, left, expr, coord=None):
        self.left = left
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.left is not None: c.append(self.left)
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_ass(self)
        for c in self.children():
            c.accept(visitor)


class In(Node):
    def __init__(self, left, expr, coord=None):
        self.left = left
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.left is not None: c.append(self.left)
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_in(self)
        for c in self.children():
            c.accept(visitor)


class Out(Node):
    def __init__(self, left, expr, coord=None):
        self.left = left
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.left is not None: c.append(self.left)
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_out(self)
        for c in self.children():
            c.accept(visitor)


class If(Node):
    def __init__(self, cond, then_stmt, else_stmt, coord=None):
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
        self.coord = coord

    def children(self):
        c = []
        if self.cond is not None: c.append(self.cond)
        if self.then_stmt is not None: c.append(self.then_stmt)
        if self.else_stmt is not None: c.append(self.else_stmt)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_if(self)
        for c in self.children():
            c.accept(visitor)


class While(Node):
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.cond is not None: c.append(self.cond)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_while(self)
        for c in self.children():
            c.accept(visitor)


class For(Node):
    def __init__(self, var, init, bound, stmt, coord=None):
        self.var = var
        self.init = init
        self.bound = bound
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.var is not None: c.append(self.var)
        if self.init is not None: c.append(self.init)
        if self.bound is not None: c.append(self.bound)
        if self.stmt is not None: c.append(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_for(self)
        for c in self.children():
            c.accept(visitor)


class On(Node):
    def __init__(self, core, pcall, coord=None):
        self.core = core
        self.pcall = pcall
        self.coord = coord

    def children(self):
        c = []
        if self.core is not None: c.append(self.core)
        if self.pcall is not None: c.append(self.pcall)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_on(self)
        for c in self.children():
            c.accept(visitor)


class Connect(Node):
    def __init__(self, left, core, dest, coord=None):
        self.left = left
        self.core = core
        self.dest = dest
        self.coord = coord

    def children(self):
        c = []
        if self.left is not None: c.append(self.left)
        if self.core is not None: c.append(self.core)
        if self.dest is not None: c.append(self.dest)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_connect(self)
        for c in self.children():
            c.accept(visitor)


class Aliases(Node):
    def __init__(self, left, name, expr, coord=None):
        self.left = left
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.left is not None: c.append(self.left)
        if self.name is not None: c.append(self.name)
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_aliases(self)
        for c in self.children():
            c.accept(visitor)


class Return(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_return(self)
        for c in self.children():
            c.accept(visitor)


class Seq(Node):
    def __init__(self, stmt, coord=None):
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.stmt is not None: c.extend(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_seq(self)
        for c in self.children():
            c.accept(visitor)


class Par(Node):
    def __init__(self, stmt, coord=None):
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.stmt is not None: c.extend(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_par(self)
        for c in self.children():
            c.accept(visitor)


class ExprList(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.extend(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_exprlist(self)
        for c in self.children():
            c.accept(visitor)


class Unary(Node):
    def __init__(self, op, elem, coord=None):
        self.op = op
        self.elem = elem
        self.coord = coord

    def children(self):
        c = []
        if self.elem is not None: c.append(self.elem)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_unary(self)
        for c in self.children():
            c.accept(visitor)


class Binop(Node):
    def __init__(self, op, elem, right, coord=None):
        self.op = op
        self.elem = elem
        self.right = right
        self.coord = coord

    def children(self):
        c = []
        if self.elem is not None: c.append(self.elem)
        if self.right is not None: c.append(self.right)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_binop(self)
        for c in self.children():
            c.accept(visitor)


class Group(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_group(self)
        for c in self.children():
            c.accept(visitor)


class Sub(Node):
    def __init__(self, name, expr, coord=None):
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.name is not None: c.append(self.name)
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_sub(self)
        for c in self.children():
            c.accept(visitor)


class Fcall(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        c = []
        if self.name is not None: c.append(self.name)
        if self.args is not None: c.append(self.args)
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_fcall(self)
        for c in self.children():
            c.accept(visitor)


class Number(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_number(self)
        for c in self.children():
            c.accept(visitor)


class Boolean(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_boolean(self)
        for c in self.children():
            c.accept(visitor)


class String(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_string(self)
        for c in self.children():
            c.accept(visitor)


class Char(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_char(self)
        for c in self.children():
            c.accept(visitor)


class Id(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        visitor.visit_id(self)
        for c in self.children():
            c.accept(visitor)


