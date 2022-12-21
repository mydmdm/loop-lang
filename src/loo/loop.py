from loo.abs import *


class Loop(Expression):
    """ [category, name, start, stop, step, <body>]
    children:
        [start, stop, step, body]
    """
    categories = {'loop': 5}
    attributes = {'name': 1}

    def __init__(self, name:str, dim: List[Union[int, str]]) -> None:
        tokens = tuple(['loop', name] + self.parse_range(dim))
        super().__init__(tokens)
        # self.name = name
        # self.children = [Expression.parse(d) for d in self.parse_range(dim)]
        self.children.append(Scope())

    @property
    def body(self) -> Scope:
        return self.children[3]

    @property
    def lowerb(self) -> Scope:
        return self.children[0]

    @property
    def upperb(self) -> Scope:
        return self.children[1]

    @property
    def step(self) -> Scope:
        return self.children[2]

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

    def split(self, interval: Union[int,str], out_order: str=None):
        pass

    def as_str(self, level:int) -> str:
        s = f'for(auto {self.name}={self.lowerb}; {self.name}<{self.upperb}; {self.name} += {self.step})'
        return self._code_line(level, s) + '\n' + self.body.as_str(level) + '\n'