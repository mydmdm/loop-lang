from __future__ import annotations
import abc
from typing import Dict, Optional, List, Union

from loo.utils.parser import astree

__context__ = None # type: Scope


class Expression(abc.ABC):
        
        def __init__(self, code: str) -> None:
            super().__init__()
            self.code = code
            self.grammer, self.ast = astree(code)


class Statement(abc.ABC):
    
    def __init__(self, statement: Union[str, Scope]) -> None:
        super().__init__()
        if isinstance(statement, str):
            __context__.add_statement(statement=Expression(statement))
        else:
            __context__.add_statement(statement=statement)


class Variable(abc.ABC):
    
    def __init__(self, name: str, _type: Optional[str]='int') -> None:
        super().__init__()
        self.name = name
        self.type = _type
        # self.value = value
        print(__context__)
        __context__.add_variable(variable=self)


class Scope(abc.ABC):
    
    def __init__(self, parent: Optional[Scope]=None) -> None:
        super().__init__()
        self.parent = parent # type: Optional[Scope]
        # newly declared variables that belonging to this scope
        self.variables = {} # type: Dict[str, Variable]
        self.statements = [] # type: List[Union[Expression, Scope]]

    def add_statement(self, statement: Union[Expression, Scope]) -> None:
        self.statements.append(statement)

    def add_variable(self, variable: Variable) -> None:
        assert variable.name not in self.variables, f'Variable {variable.name} already declared in this scope'
        self.variables[variable.name] = variable






class Loop(Scope):

    def __init__(self, name:str, *args: int) -> None:
        super().__init__()
        if len(args) == 1:
            self.lower, self.upper, self.step = 0, args[0], 1
        elif len(args) == 2:
            self.lower, self.upper, self.step = args[0], args[1], 1
        elif len(args) == 3:
            self.lower, self.upper, self.step = args[0], args[1], args[2]
        else:
            raise ValueError('Dimension must have 1, 2 or 3 arguments', args)
        __context__.add_variable(variable=Variable(name=name, _type='int'))
        


class NestedLoop():
    
    def __init__(self, parent: Scope) -> None:
        super().__init__()
        self.parent = parent


def set_context(ctx :Optional[Scope] = None) -> Scope:
    global __context__
    __context__ = ctx if ctx is not None else Scope()
    return __context__
