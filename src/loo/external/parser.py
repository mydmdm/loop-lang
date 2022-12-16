"""Parser for the language based on the example of PLY.
gammar of tensor language

assignment : object ASSIGN expression
           | object ACCU expression

expression : term PLUS term
           | term MINUS term
           | term TIMES term
           | term DIVIDE term
           | term
           | expression COMMA expression

term : object
     | NUMBER
     | PLUS term
     | MINUS term
     | LPAREN expression RPAREN

object : NAME
       | NAME LBRAK expression RBRAK

"""


from .ply.lex import lex
from .ply.yacc import yacc
# from anytree import AnyNode, NodeMixin, RenderTree
from typing import Optional, Iterable, Tuple

# --- Tokenizer

# All tokens must be named in advance.
tokens = ( 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
           'LPAREN', 'RPAREN', 'LBRAK', 'RBRAK', 'COMMA', #'COLON',
           'NAME', 'NUMBER', 'ASSIGN', 'ACCU' )

# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRAK = r'\['
t_RBRAK = r'\]'
t_COMMA = r'\,'
# t_COLON = r'\:'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_ASSIGN = r'\='
t_ACCU = r'\+\='

# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# Build the lexer object
lexer = lex()
    
# --- Parser

# Write functions for each grammar rule which is
# specified in the docstring.

precedence = (
    ('left', 'COMMA'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_expression(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | expression COMMA expression
               | object ASSIGN expression
               | object ACCU expression
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : term PLUS term
    #   p[0]     : p[1] p[2] p[3]
    # 
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]

def p_term_object(p):
    '''
    term : object
    '''
    p[0] = p[1]

def p_term_number(p):
    '''
    term : NUMBER
    '''
    p[0] = ('number', p[1])

def p_term_unary(p):
    '''
    term : PLUS term
         | MINUS term
    '''
    p[0] = ('unary', p[1], p[2])

def p_term_grouped(p):
    '''
    term : LPAREN expression RPAREN
    '''
    p[0] = ('grouped', p[2])

def p_object_name(p):
    '''
    object : NAME
    '''
    p[0] = ('identifier', p[1])

def p_object_index(p):
    '''
    object : NAME LBRAK expression RBRAK
    '''
    p[0] = ('index', p[1], p[3])

def p_error(p):
    print(f'Syntax error at {p.value!r}')

# Build the parser
parser = yacc()




# Parse an expression
# if __name__=='__main__':
#     for code in [
#         'a = 1 + 2 * (4+x)',
#         'a[i,j] += a[i-1,j] + 1',
#         'A[i] = B[i]',
#         'C[m,n] += A[m,k] * B[k,n]',
#     ]:
#         g, n = astree(code)
#         print(code)
#         print(RenderTree(n))
