from common.escape import Escape
import ast.ast as ast
import analysis.semantics as semantics
import analysis.children as children

def generate(ast, sem, child, 
        target_system, num_cores, 
        translate_only, compile_only):
    
    # Translate the AST
    translate_buf = translate_ast(ast, child)
    
    if translate_only:
         raise Escape()

    # Compile, assemble and link with the runtime
    builder(sem, translate_buf, outfile, a.compile_only)

def translate_ast(ast, sem, child):
    """ Transform an AST into XC 
    """
    verbose_msg("Translating AST\n")
    translate_buf = io.StringIO()
    walker = translate.Translate(sem, child, translate_buf)
    walker.walk_program(ast)
    if translate_only:
        util.write_file(outfile, translate_buf.getvalue())
    return translate_buf

def builder(sem, translate_buf, outfile, compile_only):
    """ Build the program executable 
    """
    verbose_msg('[Building an executable for {} cores]\n'
            .format(num_cores))

    builder = build.Build(num_cores, sem, verbose, show_calls)

    if compile_only:
        builder.compile_only(translate_buf, outfile, device)
    else:
        builder.run(translate_buf, outfile, device)

    verbose_msg('Produced file: '+outfile+'\n')


