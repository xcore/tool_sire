import ast

class NodeWalker(object):

    # This should be implemented as double dispatch
    def stmt(self, node, d):
        if   isinstance(node, ast.Seq):     return self.v_seq(node, d)
        elif isinstance(node, ast.Par):     return self.v_par(node, d)
        elif isinstance(node, ast.Skip):    return self.v_skip(node, d)
        elif isinstance(node, ast.Pcall):   return self.v_pcall(node, d)
        elif isinstance(node, ast.Ass):     return self.v_ass(node, d)
        elif isinstance(node, ast.In):      return self.v_in(node, d)
        elif isinstance(node, ast.Out):     return self.v_out(node, d)
        elif isinstance(node, ast.If):      return self.v_if(node, d)
        elif isinstance(node, ast.While):   return self.v_while(node, d)
        elif isinstance(node, ast.For):     return self.v_for(node, d)
        elif isinstance(node, ast.On):      return self.v_on(node, d)
        elif isinstance(node, ast.Connect): return self.v_connect(node, d)
        elif isinstance(node, ast.Aliases): return self.v_aliases(node, d)
        elif isinstance(node, ast.Return):  return self.v_return(node, d)
        else:
            raise Exception('Invalid statement')

    def expr(self, node):
        if   isinstance(node, ast.Single): return self.v_single(node)
        elif isinstance(node, ast.Unary):  return self.v_unary(node)
        elif isinstance(node, ast.Binop):  return self.v_binop(node)
        else:
            raise Exception('Invalid expression %s' % node)

    def elem(self, node):
        if   isinstance(node, ast.Group):   return self.v_group(node)
        elif isinstance(node, ast.Sub):     return self.v_sub(node)
        elif isinstance(node, ast.Fcall):   return self.v_fcall(node)
        elif isinstance(node, ast.Number):  return self.v_number(node)
        elif isinstance(node, ast.Boolean): return self.v_boolean(node)
        elif isinstance(node, ast.String):  return self.v_string(node)
        elif isinstance(node, ast.Char):    return self.v_char(node)
        elif isinstance(node, ast.Id):      return self.v_id(node)
        else: 
            raise Exception('Invalid element: %s' % node)


