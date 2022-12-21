from __future__ import annotations
import abc
from parser import expr
from typing import Dict, Optional, List, Union, Any, Iterable, Tuple, Type
from collections import deque
from unicodedata import category

from attr import attributes
from loo.external.parser import parser
from anytree import NodeMixin, AnyNode

import logging 
logger = logging.getLogger('loo')


class _AstNode(abc.ABC):

    def __init__(self) -> None:
        super().__init__()
        self.parent = None 
        self.children = [] # type: List[_AstNode] 

    def add_children(self, nodes):
        if isinstance(nodes, _AstNode): # not list
            nodes = [nodes]
        self.children.extend(nodes)
        for n in nodes:
            n.set_parent(self)

    def set_parent(self, node: _AstNode):
        self.parent = node

    @staticmethod
    def _code_line(level: int, src: str, ind: str = '    '):
        lst = [ind] * level
        lst.append(src)
        return ''.join(lst)

    def as_str(self, level:int = 0):
        return self._code_line(level, self.__str__())

    def __str__(self) -> str:
        return super().__str__()

    def to_anytree(self):
        dic = {k:v for k,v in vars(self).items() if k not in ['parent', 'children']}
        return AnyNode(**dic, children=[n.to_anytree() for n in self.children])


class Variable(_AstNode):
    
    def __init__(self, name: str, _type: Optional[str]='int', tags: Optional[List[str]] = None, qualifiers: Optional[List[str]]=None) -> None:
        """ some special tags:
            - tensor means need to specially handle when generating code
            - virtual means no explicit declaration in code
            - iterator means it is a loop iterator
        """
        super().__init__()
        self.name = name
        self.type = _type
        self.tags = tags or []
        self.qualifiers = qualifiers or []
        

class Expression(_AstNode):
    categories = {} # type: Dict[str,int] 
                    # allowed category values
    attributes = {} # type: Dict[str,int]
                    # attributes and corresponding tokens index

    def __init__(self, tokens: Tuple) -> None:
        super().__init__()
        assert tokens[0] in self.categories, f'not allowed {category!r}'
        self.category = tokens[0]
        len_spec = self.categories[self.category]
        if isinstance(len_spec, str):
            # for example, '3+' means >= 3
            assert len_spec.endswith('+'), f'unknown len spec {len_spec!r}'
            assert len(tokens) >= int(len_spec[:-1]), f'invalid tokens len {tokens!r}'
        else:
            assert len(tokens) == len_spec, f'invalid tokens len {tokens!r}'
        for k,i in self.attributes.items():
            setattr(self, k, tokens[i])
        k = 1 + len(self.attributes)
        self.add_children([Expression.parse(x) for x in tokens[k:]])

    @staticmethod
    def parse(input: Union[int, str, Tuple], expr_types: List[Type(Expression)] = None) -> Expression:
        """
        """
        if isinstance(input, tuple):
            tokens = input
        else:
            tokens = parser.parse(str(input))
        expr_types = expr_types or __builtin_expression_types__
        for et in expr_types:
            if tokens[0] in et.categories:
                return et(tokens)
        raise ValueError(tokens)


class OperatorExpression(Expression):
    """[category, op, operand1, <operand2>]"""
    categories = {'binop': 4, 'unary': 3}
    attributes = {'operator': 1}

    def __str__(self) -> str:
        if self.category == 'binop':
            return f'{self.children[0]} {self.operator} {self.children[1]}'


class MemAccessExpression(Expression):
    """[category, name, subscription]"""
    categories = {'index': 3}
    attributes = {'name': 1}

    @property
    def addr(self):
        return self.children[0]

    def __str__(self) -> str:
        return f'{self.name}[{self.addr}]'


class ElementoryExpression(Expression):
    """[category, value]"""
    categories = {'number': 2, 'identifier': 2, 'grouped': 2}
    attributes = {'value': 1}

    def __str__(self) -> str:
        return str(self.value)


__builtin_expression_types__ = [OperatorExpression, MemAccessExpression, ElementoryExpression]


class Scope(_AstNode):
    
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, arg) -> Any:
        if isinstance(arg, (Variable, Expression, List, Tuple)):
            self.add_children(arg)
        elif isinstance(arg, str): # expression
            self.add_children(Expression.parse(arg))
        else:
            raise ValueError(f'unkown type {arg!r}')

    def as_str(self, level:int=0) -> str:
        codes = [self._code_line(level, '{')]
        codes.extend([s.as_str(level+1) for s in self.children])
        codes.append(self._code_line(level, '}'))
        return ('\n'.join(codes))


class ContextManager:

    def __init__(self) -> None:
        self.stack = deque()

    def __enter__(self):
        pass

    def __exit__(self):
        pass


