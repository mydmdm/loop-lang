from loo.abs import set_context, Variable, Statement
from loo.variables import *
from anytree import RenderTree

################################################################
# tests and examples
################################################################

ctx = set_context()

A = Variable('A', 'int')
B = Variable('B', 'int')

Statement('A[i] = B[i]')

print(RenderTree(ctx.statements[0].ast))
