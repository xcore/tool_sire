import ast

class NodeWalker(object):
    
    def __init__(self):
        self.vardecl_type = {
            'var'     : self.vardecl_var,
            'array'   : self.vardecl_array,
            'val'     : self.vardecl_val,
            'port'    : self.vardecl_port
        }

        self.param_type = {
            'var'     : self.param_var,
            'alias'   : self.param_alias,
            'val'     : self.param_val,
            'chanend' : self.param_chanend
        }

    # Define function lookups for each variable declaration form
    def vardecl_var  (self, node): pass
    def vardecl_array(self, node): pass
    def vardecl_val  (self, node): pass
    def vardecl_port (self, node): pass
    
    vardecl = lambda self, node: self.vardecl_type[node.form](node)

    # Define function lookups for each parameter form
    def param_var    (self, node): pass
    def param_alias  (self, node): pass
    def param_val    (self, node): pass
    def param_chanend(self, node): pass

    param = lambda self, node: self.param_type[node.type](node)

    # This should be implemented as double dispatch
    def stmt(self, node, d):
        if   isinstance(node, ast.Seq):     return self.stmt_seq(node, d)
        elif isinstance(node, ast.Par):     return self.stmt_par(node, d)
        elif isinstance(node, ast.Skip):    return self.stmt_skip(node, d)
        elif isinstance(node, ast.Pcall):   return self.stmt_pcall(node, d)
        elif isinstance(node, ast.Ass):     return self.stmt_ass(node, d)
        elif isinstance(node, ast.In):      return self.stmt_in(node, d)
        elif isinstance(node, ast.Out):     return self.stmt_out(node, d)
        elif isinstance(node, ast.If):      return self.stmt_if(node, d)
        elif isinstance(node, ast.While):   return self.stmt_while(node, d)
        elif isinstance(node, ast.For):     return self.stmt_for(node, d)
        elif isinstance(node, ast.On):      return self.stmt_on(node, d)
        elif isinstance(node, ast.Connect): return self.stmt_connect(node, d)
        elif isinstance(node, ast.Aliases): return self.stmt_aliases(node, d)
        elif isinstance(node, ast.Return):  return self.stmt_return(node, d)
        else:
            raise Exception('Invalid statement')

    def expr(self, node):
        if   isinstance(node, ast.Single): return self.expr_single(node)
        elif isinstance(node, ast.Unary):  return self.expr_unary(node)
        elif isinstance(node, ast.Binop):  return self.expr_binop(node)
        else:
            raise Exception('Invalid expression %s' % node)

    def elem(self, node):
        if   isinstance(node, ast.Group):   return self.elem_group(node)
        elif isinstance(node, ast.Sub):     return self.elem_sub(node)
        elif isinstance(node, ast.Fcall):   return self.elem_fcall(node)
        elif isinstance(node, ast.Number):  return self.elem_number(node)
        elif isinstance(node, ast.Boolean): return self.elem_boolean(node)
        elif isinstance(node, ast.String):  return self.elem_string(node)
        elif isinstance(node, ast.Char):    return self.elem_char(node)
        elif isinstance(node, ast.Id):      return self.elem_id(node)
        else: 
            raise Exception('Invalid element: %s' % node)

