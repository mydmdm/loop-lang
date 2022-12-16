from __future__ import annotations
import abc
from typing import Dict, Optional, List, Union, Any, Iterable, Tuple
from collections import deque
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

    def __str__(self) -> str:
        return super().__str__()

    def to_anytree(self):
        dic = {k:v for k,v in vars(self).items() if k not in ['parent', 'children']}
        return AnyNode(**dic, children=[n.to_anytree() for n in self.children])


class Variable(_AstNode):
    
    def __init__(self, name: str, _type: Optional[str]='int', tags: Optional[List[str]] = None) -> None:
        """ some special tags:
            - tensor means need to specially handle when generating code
            - virtual means no explicit declaration in code
            - iterator means it is a loop iterator
        """
        super().__init__()
        self.name = name
        self.type = _type
        self.tags = tags or []


class Expression(_AstNode):

    def __init__(self, category: str, **kwargs) -> None:
        super().__init__()
        self.category = category
        for k,v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def parse(code: Union[int, str]) -> Expression:
        if not isinstance(code, str):
            code = str(code)
        tokens = parser.parse(code)
        return Expression._to_node(tokens)

    @staticmethod
    def _to_node(tokens: Tuple[str,str]) -> Expression:
        category = tokens[0] # type: str
        dic = {} 
        children = [] # List[Tuple]
        if category in ['binop', 'unary']: # operators
            dic['operator'] = tokens[1]
            children = tokens[2:]
        elif category == 'index':
            dic['name'] = tokens[1]
            children = tokens[2:]
        elif category in ['number', 'identifier']:
            dic['value'] = tokens[1]
        elif category == 'grouped':
            pass
        else:
            raise ValueError(f'Unknown category {category!r}')
        node = Expression(category, **dic)
        node.add_children([Expression._to_node(x) for x in children])
        return node


class Loop(Expression):

    def __init__(self, name:str, dim: List[Union[int, str]]) -> None:
        """children:
            [start, stop, step, body]
        """
        super().__init__(category='loop', name=name)
        self.children = [Expression.parse(d) for d in self.parse_range(dim)]
        self.children.append(Scope())

    @property
    def body(self) -> Scope:
        return self.children[3]

    @staticmethod
    def parse_range(args):
        if len(args) == 1:
            return [0, args[0], 1]
        elif len(args) == 2:
            return [args[0], args[1], 1]
        elif len(args) == 3:
            return args
        else:
            raise ValueError('Dimension must have 1, 2 or 3 arguments', args)


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

    def __str__(self) -> str:
        codes = ['{']
        codes.extend([str(s) for s in self.children])
        codes.append('}')
        return ('\n'.join(codes))


class ContextManager:

    def __init__(self) -> None:
        self.stack = deque()

    def __enter__(self):
        pass

    def __exit__(self):
        pass


