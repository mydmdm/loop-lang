from loo.abs import *


class Loop(Expression):
    """ [category, name, start, stop, step, body]
    children:
        [start, stop, step, body]
    """
    categories = {'loop': 6}
    attributes = {'name': 1}

    def __init__(self, name:str, dim: List[Union[int, str]]) -> None:
        tokens = tuple(['loop', name] + self.parse_range(dim) + [Scope()]) # type: ignore
        super().__init__(tokens)

    @property
    def body(self) -> Scope:
        return self.children[3] #type: ignore

    @property
    def lowerb(self) -> AstNode:
        return self.children[0]

    @property
    def upperb(self) -> AstNode:
        return self.children[1]

    @property
    def step(self) -> AstNode:
        return self.children[2]

    @property
    def is_normalized(self) -> bool:
        return self.lowerb == ('number', 0) and self.step == ('number', 1)

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

    def split(self, intervals: List):
        new_dims = []
        for i,s in enumerate(intervals):
            if i==0:
                ax = Loop(f'{self.name}{i}', [self.lowerb, self.upperb, s])
            else:
                ax = Loop(f'{self.name}{i}', [0, intervals[i-1], s])
            new_dims.append(ax)
        ax = Loop(f'{self.name}{len(intervals)}', [0, intervals[-1], 1])
        new_dims.append(ax)
        return new_dims

    def as_str(self, level:int) -> str:
        s = f'for(auto {self.name}={self.lowerb}; {self.name}<{self.upperb}; {self.name} += {self.step})'
        return self._code_line(level, s) + '\n' + self.body.as_str(level) + '\n'