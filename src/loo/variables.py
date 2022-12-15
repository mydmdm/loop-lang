from loo.abs import *
from typing import List, Iterable


class Tensor(Variable):

    def __init__(self, name: str, dtype: str, shape: Iterable[int]) -> None:
        super().__init__(name, 'tensor')
        self.shape = shape
        self.dtype = dtype