# Copyright (c) 2011, James Hanlon, All rights reserved
# This software is freely distributable under a derivative of the
# University of Illinois/NCSA Open Source License posted in
# LICENSE.txt and at <http://github.xcore.com/>

import ply.yacc as yacc
import ast
import error
from lexer import Lexer
from type import Type

class Coord(object):
    """ Coordinates (file, line, col) of a syntactic element. """
    def __init__(self, file, line, column=None):
        self.file = file
        self.line = line
        self.column = column
        #print('new coord: {}:{}'.format(line, column))

    def __str__(self):
        str = "%s:%s" % (self.file, self.line)
        if self.column: str += ":%s" % self.column
        return str

class Parser(object):
    """ A parser object for the sire langauge """

    def __init__(self, error, lex_optimise=True, lextab='lextab', 
            yacc_optimise=True, yacctab='yacctab', yacc_debug=False):
        """ Create a new parser """
        self.error = error

        # Instantiate and build the lexer
        self.lexer = Lexer(error_func=self.lex_error)
        self.lexer.build(optimize=lex_optimise, lextab=lextab)
        self.tokens = self.lexer.tokens

        # Create and instantiate the parser
        self.parser = yacc.yacc(module=self, debug=yacc_debug, 
                optimize=yacc_optimise)

    def parse(self, text, filename='', debug=0):
        """ Parse a file and return the AST """
        self.lexer.filename = filename
        self.lexer.reset()
        return self.parser.parse(text, lexer=self.lexer, debug=debug,
                tracking=True)

    def coord(self, p, index=1):
        """ Return a coordinate for a production """
        return Coord(file=self.lexer.filename, line=p.lineno(index), 
                column=self.lexer.findcol(self.lexer.data(), p.lexpos(index)))
    
    def tcoord(self, t):
        """ Return a coordinate for a token """
        return Coord(file=self.lexer.filename, line=t.lineno, 
                column=self.lexer.findcol(self.lexer.data(), t.lexpos))

    def lex_error(self, msg, line, col):
        self.error.report_error(msg, Coord(line, col))
        self.lexer.errok()

    def parse_error(self, msg, coord=None, discard=True):
        self.error.report_error(msg, coord)
        if discard: self.parser.errok()

    # Define operator presidence
    precedence = (
        ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE'), 
        ('left', 'LSHIFT', 'RSHIFT'),
        ('left', 'AND', 'OR', 'XOR', 'REM', 'LOR', 'LAND'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('right', 'UMINUS', 'UNOT')
    )

    start = 'program'

    # Program declaration ======================================
    
    def p_program(self, p):
        'program : var_decls proc_decls'
        p[0] = ast.Program(p[1], p[2], self.coord(p, 1))

    # Program declaration error
    def p_program_error(self, p):
        'program : error'
        self.parse_error('Syntax error', p, 1)
        p[0] = None

    # Variable declarations ====================================

    def p_var_decls(self, p):
        '''var_decls : empty
                     | var_decl_seq'''
        p[0] = ast.Decls(p[1] if len(p)==2 else None, self.coord(p))

    # Variable declaration sequence (return a single list)
    def p_var_decl_seq(self, p):
        '''var_decl_seq : var_decl SEMI
                        | var_decl SEMI var_decl_seq'''
        p[0] = [p[1]] if len(p)==3 else [p[1]] + p[3]

    # Variable declaration sequence error
    def p_var_decl_seq_err(self, p):
        'var_decl_seq : error SEMI'
        print('Syntax error at line {}:{}'.format(
                p.lineno(1), p.lexpos(1)))

    # Var declaration
    def p_var_decl_var(self, p):
        'var_decl : type name'
        p[0] = ast.Decl(p[2], Type(p[1], 'single'), None, 
                self.coord(p))

    # Array declaration
    def p_var_decl_array(self, p):
        '''var_decl : type name LBRACKET RBRACKET
                    | type name LBRACKET expr RBRACKET'''
        p[0] = ast.Decl(p[2], 
                Type(p[1], 'array' if len(p)==6 else 'alias'), 
                p[4] if len(p)==6 else None, self.coord(p))

    # Val declaration
    def p_var_decl_val(self, p):
        'var_decl : VAL name ASS expr'
        p[0] = ast.Decl(p[2], Type('val', 'single'), p[4], 
                self.coord(p))

    # Port declaration
    def p_var_decl_port(self, p):
        'var_decl : PORT name COLON expr'
        p[0] = ast.Decl(p[2], Type('port', 'single'), p[4], 
                self.coord(p))

    # Variable types
    def p_type_id(self, p):
        '''type : VAR
                | CHAN'''
        p[0] = p[1]

    # Procedure declarations ===================================

    def p_proc_decls(self, p):
        '''proc_decls : proc_decl_seq
                      | empty'''
        p[0] = ast.Defs(p[1] if len(p)==2 else None, self.coord(p))

    # Procedure sequence (return a single list)
    def p_proc_decl_seq(self, p):
        '''proc_decl_seq : proc_decl
                         | proc_decl proc_decl_seq'''
        p[0] = [p[1]] if len(p)==2 else [p[1]] + p[2]

    # Process
    def p_proc_decl_proc(self, p):
        'proc_decl : PROC name LPAREN formals RPAREN IS var_decls stmt'
        p[0] = ast.Def(p[2], Type('proc', 'procedure'), 
                p[4], p[7], p[8], self.coord(p)) 

    # Function
    def p_proc_decl_func(self, p):
        'proc_decl : FUNC name LPAREN formals RPAREN IS var_decls stmt'
        p[0] = ast.Def(p[2],  Type('func', 'procedure'),
                p[4], p[7], p[8], self.coord(p)) 

    # Procedure error
    def p_proc_decl_proc_err(self, p):
        '''proc_decl : PROC error IS var_decls stmt'''
        self.parse_error('process declaration', p, 2)

    # Function error
    def p_proc_decl_func_err(self, p):
        '''proc_decl : FUNC error IS var_decls stmt'''
        self.parse_error('function declaration', p, 2)

    # Formal declarations ======================================

    def p_formals(self, p):
        '''formals : empty
                   | formals_seq'''
        p[0] = ast.Formals(p[1] if len(p)==2 else None, self.coord(p))

    # Formal parameter sequence (return a single list)
    def p_formals_seq(self, p):
        '''formals_seq : param_decl
                       | param_decl COMMA formals_seq'''
        p[0] = [p[1]] if len(p)==2 else [p[1]] + p[3]

    # Var parameter
    def p_param_decl_var(self, p):
        'param_decl : name'
        p[0] = ast.Param(p[1], Type('var', 'single'), None,
                self.coord(p))

    # Array alias parameter
    def p_param_decl_alias(self, p):
        'param_decl : name LBRACKET name RBRACKET'
        p[0] = ast.Param(p[1], Type('var', 'alias'), 
                ast.ExprSingle(ast.ElemId(p[3])),
                self.coord(p))

    # Val parameter
    def p_param_decl_val(self, p):
        'param_decl : VAL name'
        p[0] = ast.Param(p[2], Type('val', 'single'), None,
                self.coord(p))

    # Chanend parameter
    def p_param_decl_chanend(self, p):
        'param_decl : CHANEND name'
        p[0] = ast.Param(p[2], Type('chanend', 'single'), None,
                self.coord(p))

    # Statement blocks =========================================
    
    # Seq block
    def p_stmt_seq_block(self, p):
        'stmt : START stmt_seq END'
        p[0] = ast.StmtSeq(p[2], self.coord(p))

    # Seq
    def p_stmt_seq(self, p):
        '''stmt_seq : stmt
                    | stmt SEMI stmt_seq'''
        p[0] = [p[1]] if len(p)==2 else [p[1]] + p[3]

    # Par block
    def p_stmt_par_block(self, p):
        'stmt : START stmt_par END'
        p[0] = ast.StmtPar(p[2], self.coord(p))

    # Par
    def p_stmt_par(self, p):
        '''stmt_par : stmt BAR stmt'''
        p[0] = [p[1]] + [p[3]]

    def p_stmt_par_seq(self, p):
        '''stmt_par : stmt BAR stmt_par'''
        p[0] = [p[1]] + p[3]

    # Seq error
    def p_stmt_seq_err(self, p):
        'stmt_seq : error SEMI'
        self.parse_error('sequential block', self.coord(p))

    # Par error
    def p_stmt_par_err(self, p):
        'stmt_par : error BAR'
        self.parse_error('parallel block', self.coord(p))

    # Statements ==========================================

    def p_stmt_skip(self, p):
        'stmt : SKIP'
        p[0] = ast.StmtSkip(self.coord(p))

    def p_stmt_pcall(self, p):
        'stmt : name LPAREN expr_list RPAREN'
        p[0] = ast.StmtPcall(p[1], p[3], self.coord(p))

    def p_stmt_ass(self, p):
        'stmt : left ASS expr'
        p[0] = ast.StmtAss(p[1], p[3], self.coord(p))

    def p_stmt_in(self, p):
        'stmt : left IN expr'
        p[0] = ast.StmtIn(p[1], p[3], self.coord(p))

    def p_stmt_out(self, p):
        'stmt : left OUT expr'
        p[0] = ast.StmtOut(p[1], p[3], self.coord(p))

    def p_stmt_if(self, p):
        'stmt : IF expr THEN stmt ELSE stmt'
        p[0] = ast.StmtIf(p[2], p[4], p[6], self.coord(p))

    def p_stmt_while(self, p):
        'stmt : WHILE expr DO stmt'
        p[0] = ast.StmtWhile(p[2], p[4], self.coord(p))

    def p_stmt_for(self, p):
        'stmt : FOR left ASS expr STEP expr UNTIL expr DO stmt'
        p[0] = ast.StmtFor(p[2], p[4], p[6], p[8], p[10])

    def p_stmt_on(self, p):
        'stmt : ON left DO name LPAREN expr_list RPAREN'
        p[0] = ast.StmtOn(p[2], 
                ast.ElemPcall(p[4], p[6], self.coord(p)), 
                self.coord(p))

    def p_stmt_connect(self, p):
        'stmt : CONNECT left TO left COLON left'
        p[0] = ast.StmtConnect(p[2], p[4], p[6], self.coord(p))

    def p_stmt_aliases(self, p):
        'stmt : name ALIASES name LBRACKET expr DOTS RBRACKET'
        p[0] = ast.StmtAliases(p[1], p[3], p[5], self.coord(p))

    def p_stmt_return(self, p):
        'stmt : RETURN expr'
        p[0] = ast.StmtReturn(p[2], self.coord(p))

    # Expressions ==============================================

    def p_expr_list(self, p):
        '''expr_list : empty
                     | expr_seq'''
        p[0] = ast.ExprList(p[1] if p[1] else [], self.coord(p))

    def p_expr_seq(self, p):
        '''expr_seq : expr
                    | expr COMMA expr_seq'''
        p[0] = [p[1]] if len(p)==2 else [p[1]] + p[3]

    def p_expr_sinle(self, p):
        'expr : elem' 
        p[0] = ast.ExprSingle(p[1])

    def p_expr_unary(self, p):
        '''expr : MINUS elem %prec UMINUS
                | NOT elem %prec UNOT'''
        p[0] = ast.ExprUnary(p[1], p[2] if len(p)>2 else None, self.coord(p))

    def p_expr_binary_arithmetic(self, p):
        '''expr : elem PLUS right
                | elem MINUS right
                | elem MULT right
                | elem DIV right
                | elem REM right
                | elem OR right
                | elem AND right
                | elem XOR right
                | elem LOR right
                | elem LAND right
                | elem LSHIFT right
                | elem RSHIFT right'''
        p[0] = ast.ExprBinop(p[2], p[1], p[3], self.coord(p))

    def p_expr_binary_relational(self, p):
        '''expr : elem LT right
                | elem GT right
                | elem LE right
                | elem GE right
                | elem EQ right
                | elem NE right'''
        p[0] = ast.ExprBinop(p[2], p[1], p[3], self.coord(p))

    def p_right_sinle(self, p):
        'right : elem'
        p[0] = ast.ExprSingle(p[1])

    # Associative operators, TODO: check these
    def p_right(self, p):
        '''right : elem AND right
                 | elem OR right
                 | elem XOR right
                 | elem PLUS right
                 | elem MINUS right'''
                 # MULT and DIV?
        p[0] = ast.ExprBinop(p[2], p[1], p[3], self.coord(p))

    # Elements =================================================
    
    def p_elem_group(self, p):
        'elem : LPAREN expr RPAREN'
        p[0] = ast.ElemGroup(p[2], self.coord(p))

    def p_left_name(self, p):
        'left : name'
        p[0] = ast.ElemId(p[1], self.coord(p)) 
     
    def p_left_sub(self, p):
        'left : name LBRACKET expr RBRACKET'
        p[0] = ast.ElemSub(p[1], p[3], self.coord(p))

    def p_elem_name(self, p):
        'elem : name'
        p[0] = ast.ElemId(p[1], self.coord(p)) 

    def p_elem_sub(self, p):
        'elem : name LBRACKET expr RBRACKET'
        p[0] = ast.ElemSub(p[1], p[3], self.coord(p))

    def p_elem_fcall(self, p):
        'elem : name LPAREN expr_list RPAREN'
        p[0] = ast.ElemFcall(p[1], p[3], self.coord(p))

    def p_elem_number(self, p):
        '''elem : HEXLITERAL
                | DECLITERAL
                | BINLITERAL'''
        p[0] = ast.ElemNumber(p[1], self.coord(p))

    def p_elem_boolean_true(self, p):
        'elem : TRUE'
        p[0] = ast.ElemBoolean(p[1], self.coord(p))

    def p_elem_boolean_false(self, p):
        'elem : FALSE'
        p[0] = ast.ElemBoolean(p[1], self.coord(p))

    def p_elem_string(self, p):
        'elem : STRING'
        p[0] = ast.ElemString(p[1], self.coord(p))

    def p_elem_char(self, p):
        'elem : CHAR'
        p[0] = ast.ElemChar(p[1], self.coord(p))

    # Identifier ==========================================

    def p_name(self, p):
        'name : ID'
        p[0] = p[1]

    # Empty rule
    def p_empty(self, p):
        'empty :'
        pass
    
    # Error rule for syntax errors
    def p_error(self, t):
        if t:
            self.parse_error('before: {}'.format(t.value), self.tcoord(t))
        else:
            self.parse_error('at end of input', discard=False)

