class Node(object):
    def __init__(self, lineno=0, coloff=0):
        self.lineno = lineno
        self.coloff = coloff

    def accept(self, visitor):
        pass

class Program(Node):
    def __init__(self, lineno, coloff, var_decls, proc_decls):
        super(Program, self).__init__(lineno, coloff)
        self.var_decls = var_decls
        self.proc_decls = proc_decls

    def accept(self, visitor):
        visitor.visit_program(self)
        self.var_decls.accept(visitor)
        self.proc_decls.accept(visitor)

class VarDecls(Node):
    def __init__(self, lineno, coloff, decl, next):
        super(VarDecls, self).__init__(lineno, coloff)
        self.decl = decl
        self.next = next

    def accept(self, visitor):
        self.decl.accept(visitor)
        if self.next: 
            self.next.accept(visitor)

class VarDecl(Node):
    def __init__(self, lineno, coloff, form, type, name, expr=None):
        super(VarDecl, self).__init__(lineno, coloff)
        self.form = form
        self.type = type
        self.name = name
        self.expr = expr

    def accept(self, visitor):
        #self.name.accept(visitor)
        #self.expr.accept(visitor)
        visitor.visit_var_decl(self)

class ProcDecls(Node):
    def __init__(self, lineno, coloff, decl, next):
        super(ProcDecls, self).__init__(lineno, coloff)
        self.decl = decl
        self.next = next

    def accept(self, visitor):
        self.decl.accept(visitor)
        if self.next: 
            self.next.accept(visitor)

class ProcDecl(Node):
    def __init__(self, lineno, coloff, type, name, formals, var_decls, stmt):
        super(ProcDecl, self).__init__(lineno, coloff)
        self.type = type
        self.name = name
        self.formals = formals
        self.var_decls = var_decls
        self.stmt = stmt

    def accept(self, visitor):
        #self.name.accept(visitor)
        #self.expr.accept(visitor)
        visitor.visit_proc_decl(self)

# Generic Node visitor base class
class NodeVisitor(object):

    def visit(self, node):
        pass

    def generic_visit():
        pass

