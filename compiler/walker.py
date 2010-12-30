import ast
import util

class NodeWalker(object):
    
    def vardecl(self, node, d):
        'self.{}'.format(util.camel_to_under(node.__class__.__name__))(node, d)
    
    def param(self, node):
        'self.{}'.format(util.camel_to_under(node.__class__.__name__))(node)
    
    def stmt(self, node, d):
        'self.{}'.format(util.camel_to_under(node.__class__.__name__))(node, d)
    
    def expr(self, node):
        'self.{}'.format(util.camel_to_under(node.__class__.__name__))(node)

    def elem(self, node):
        'self.{}'.format(util.camel_to_under(node.__class__.__name__))(node)



    def vardecl_(self, node, d):
        if   isinstance(node, ast.VarDecl):   return self.decl_var(node, d)
        elif isinstance(node, ast.ArrayDecl): return self.decl_array(node, d)
        elif isinstance(node, ast.ValDecl):   return self.decl_val(node, d)
        elif isinstance(node, ast.PortDecl):  return self.decl_port(node, d)
        else:
            raise Exception('Invalid variable declaration')

    def param_(self, node):
        if   isinstance(node, ast.VarParam):     return self.param_var(node, d)
        elif isinstance(node, ast.AliasParam):   return self.param_alias(node, d)
        elif isinstance(node, ast.ValParam):     return self.param_val(node, d)
        elif isinstance(node, ast.ChanendParam): return self.param_chanend(node, d)
        else:
            raise Exception('Invalid parameter')

    def stmt_(self, node, d):
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

    def expr_(self, node):
        if   isinstance(node, ast.Single): return self.expr_single(node)
        elif isinstance(node, ast.Unary):  return self.expr_unary(node)
        elif isinstance(node, ast.Binop):  return self.expr_binop(node)
        else:
            raise Exception('Invalid expression %s' % node)

    def elem_(self, node):
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

