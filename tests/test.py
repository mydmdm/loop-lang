from loo.abs import Expression, Variable, logger, Scope
from loo.loop import Loop
from loo.variables import *
from anytree import RenderTree

logging.basicConfig(level=logging.DEBUG)

################################################################
# tests and examples
################################################################

ctx = Scope()

ctx([Variable(i, 'int') for i in ('M', 'N', 'K')])

i = Loop('i', ['M'])
j = Loop('j', ['N'])
k = Loop('k', ['K'])

ctx(i)
i.body(j)
j.body(k)
k.body('C[i,j] += A[i,k] * B[k,j]')

print(ctx.as_str(0))
print(RenderTree(ctx.to_anytree()))
