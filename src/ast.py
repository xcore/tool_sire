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
    def visit_program(self, node): pass
    def visit_decls(self, node): pass
    def visit_decl(self, node): pass
    def visit_defs(self, node): pass
    def visit_def(self, node): pass
    def visit_formals(self, node): pass
    def visit_param(self, node): pass
    def visit_stmt_seq(self, node): pass
    def visit_stmt_par(self, node): pass
    def visit_stmt_skip(self, node): pass
    def visit_stmt_pcall(self, node): pass
    def visit_stmt_ass(self, node): pass
    def visit_stmt_alias(self, node): pass
    def visit_stmt_if(self, node): pass
    def visit_stmt_while(self, node): pass
    def visit_stmt_for(self, node): pass
    def visit_stmt_rep(self, node): pass
    def visit_stmt_on(self, node): pass
    def visit_stmt_connect(self, node): pass
    def visit_stmt_return(self, node): pass
    def visit_expr_list(self, node): pass
    def visit_expr_single(self, node): pass
    def visit_expr_unary(self, node): pass
    def visit_expr_binop(self, node): pass
    def visit_elem_group(self, node): pass
    def visit_elem_sub(self, node): pass
    def visit_elem_slice(self, node): pass
    def visit_elem_fcall(self, node): pass
    def visit_elem_pcall(self, node): pass
    def visit_elem_number(self, node): pass
    def visit_elem_boolean(self, node): pass
    def visit_elem_string(self, node): pass
    def visit_elem_char(self, node): pass
    def visit_elem_id(self, node): pass


class Program(Node):
    def __init__(self, decls, defs, coord=None):
        self.decls = decls
        self.defs = defs
        self.coord = coord

    def children(self):
        c = []
        if self.decls is not None: c.append(self.decls)
        if self.defs is not None: c.append(self.defs)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_program(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Program('
        s += ')'
        return s

class Decls(Node):
    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord

    def children(self):
        c = []
        if self.decl is not None: c.extend(self.decl)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_decls(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Decls('
        s += ')'
        return s

class Decl(Node):
    def __init__(self, name, type, expr, coord=None):
        self.name = name
        self.type = type
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_decl(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Decl('
        s += ', '.join('%s' % v for v in [self.name, self.type, self.expr])
        s += ')'
        return s

class Defs(Node):
    def __init__(self, decl, coord=None):
        self.decl = decl
        self.coord = coord

    def children(self):
        c = []
        if self.decl is not None: c.extend(self.decl)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_defs(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Defs('
        s += ')'
        return s

class Def(Node):
    def __init__(self, name, type, formals, decls, stmt, coord=None):
        self.name = name
        self.type = type
        self.formals = formals
        self.decls = decls
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.formals is not None: c.append(self.formals)
        if self.decls is not None: c.append(self.decls)
        if self.stmt is not None: c.append(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_def(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Def('
        s += ', '.join('%s' % v for v in [self.name, self.type])
        s += ')'
        return s

class Formals(Node):
    def __init__(self, params, coord=None):
        self.params = params
        self.coord = coord

    def children(self):
        c = []
        if self.params is not None: c.extend(self.params)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_formals(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Formals('
        s += ')'
        return s

class Param(Node):
    def __init__(self, name, type, expr, coord=None):
        self.name = name
        self.type = type
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_param(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'Param('
        s += ', '.join('%s' % v for v in [self.name, self.type, self.expr])
        s += ')'
        return s

class StmtSeq(Node):
    def __init__(self, stmt, coord=None):
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.stmt is not None: c.extend(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_seq(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtSeq('
        s += ')'
        return s

class StmtPar(Node):
    def __init__(self, pcall, coord=None):
        self.pcall = pcall
        self.coord = coord

    def children(self):
        c = []
        if self.pcall is not None: c.extend(self.pcall)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_par(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtPar('
        s += ')'
        return s

class StmtSkip(Node):
    def __init__(self, coord=None):
        self.coord = coord

    def children(self):
        return ()

    def accept(self, visitor):
        tag = visitor.visit_stmt_skip(self)
        visitor.down(tag)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtSkip('
        s += ')'
        return s

class StmtPcall(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        c = []
        if self.args is not None: c.append(self.args)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_pcall(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtPcall('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

class StmtAss(Node):
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
        tag = visitor.visit_stmt_ass(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtAss('
        s += ')'
        return s

class StmtAlias(Node):
    def __init__(self, dest, name, begin, end, coord=None):
        self.dest = dest
        self.name = name
        self.begin = begin
        self.end = end
        self.coord = coord

    def children(self):
        c = []
        if self.begin is not None: c.append(self.begin)
        if self.end is not None: c.append(self.end)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_alias(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtAlias('
        s += ', '.join('%s' % v for v in [self.dest, self.name])
        s += ')'
        return s

class StmtIf(Node):
    def __init__(self, cond, thenstmt, elsestmt, coord=None):
        self.cond = cond
        self.thenstmt = thenstmt
        self.elsestmt = elsestmt
        self.coord = coord

    def children(self):
        c = []
        if self.cond is not None: c.append(self.cond)
        if self.thenstmt is not None: c.append(self.thenstmt)
        if self.elsestmt is not None: c.append(self.elsestmt)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_if(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtIf('
        s += ')'
        return s

class StmtWhile(Node):
    def __init__(self, cond, stmt, coord=None):
        self.cond = cond
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.cond is not None: c.append(self.cond)
        if self.stmt is not None: c.append(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_while(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtWhile('
        s += ')'
        return s

class StmtFor(Node):
    def __init__(self, var, init, bound, step, stmt, coord=None):
        self.var = var
        self.init = init
        self.bound = bound
        self.step = step
        self.stmt = stmt
        self.coord = coord

    def children(self):
        c = []
        if self.var is not None: c.append(self.var)
        if self.init is not None: c.append(self.init)
        if self.bound is not None: c.append(self.bound)
        if self.step is not None: c.append(self.step)
        if self.stmt is not None: c.append(self.stmt)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_for(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtFor('
        s += ')'
        return s

class StmtRep(Node):
    def __init__(self, var, init, count, pcall, coord=None):
        self.var = var
        self.init = init
        self.count = count
        self.pcall = pcall
        self.coord = coord

    def children(self):
        c = []
        if self.var is not None: c.append(self.var)
        if self.init is not None: c.append(self.init)
        if self.count is not None: c.append(self.count)
        if self.pcall is not None: c.append(self.pcall)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_rep(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtRep('
        s += ')'
        return s

class StmtOn(Node):
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
        tag = visitor.visit_stmt_on(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtOn('
        s += ')'
        return s

class StmtConnect(Node):
    def __init__(self, src, core, dest, coord=None):
        self.src = src
        self.core = core
        self.dest = dest
        self.coord = coord

    def children(self):
        c = []
        if self.core is not None: c.append(self.core)
        if self.dest is not None: c.append(self.dest)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_connect(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtConnect('
        s += ', '.join('%s' % v for v in [self.src])
        s += ')'
        return s

class StmtReturn(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_stmt_return(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'StmtReturn('
        s += ')'
        return s

class ExprList(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.extend(self.expr)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_expr_list(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ExprList('
        s += ')'
        return s

class ExprSingle(Node):
    def __init__(self, elem, coord=None):
        self.elem = elem
        self.coord = coord

    def children(self):
        c = []
        if self.elem is not None: c.append(self.elem)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_expr_single(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ExprSingle('
        s += ')'
        return s

class ExprUnary(Node):
    def __init__(self, op, elem, coord=None):
        self.op = op
        self.elem = elem
        self.coord = coord

    def children(self):
        c = []
        if self.elem is not None: c.append(self.elem)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_expr_unary(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ExprUnary('
        s += ', '.join('%s' % v for v in [self.op])
        s += ')'
        return s

class ExprBinop(Node):
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
        tag = visitor.visit_expr_binop(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ExprBinop('
        s += ', '.join('%s' % v for v in [self.op])
        s += ')'
        return s

class ElemGroup(Node):
    def __init__(self, expr, coord=None):
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_group(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemGroup('
        s += ')'
        return s

class ElemSub(Node):
    def __init__(self, name, expr, coord=None):
        self.name = name
        self.expr = expr
        self.coord = coord

    def children(self):
        c = []
        if self.expr is not None: c.append(self.expr)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_sub(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemSub('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

class ElemSlice(Node):
    def __init__(self, name, begin, end, coord=None):
        self.name = name
        self.begin = begin
        self.end = end
        self.coord = coord

    def children(self):
        c = []
        if self.begin is not None: c.append(self.begin)
        if self.end is not None: c.append(self.end)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_slice(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemSlice('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

class ElemFcall(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        c = []
        if self.args is not None: c.append(self.args)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_fcall(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemFcall('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

class ElemPcall(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        c = []
        if self.args is not None: c.append(self.args)
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_pcall(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemPcall('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

class ElemNumber(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_number(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemNumber('
        s += ', '.join('%s' % v for v in [self.value])
        s += ')'
        return s

class ElemBoolean(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_boolean(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemBoolean('
        s += ', '.join('%s' % v for v in [self.value])
        s += ')'
        return s

class ElemString(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_string(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemString('
        s += ', '.join('%s' % v for v in [self.value])
        s += ')'
        return s

class ElemChar(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_char(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemChar('
        s += ', '.join('%s' % v for v in [self.value])
        s += ')'
        return s

class ElemId(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        c = []
        return tuple(c)

    def accept(self, visitor):
        tag = visitor.visit_elem_id(self)
        visitor.down(tag)
        for c in self.children():
            c.accept(visitor)
        visitor.up(tag)

    def __repr__(self):
        s =  'ElemId('
        s += ', '.join('%s' % v for v in [self.name])
        s += ')'
        return s

