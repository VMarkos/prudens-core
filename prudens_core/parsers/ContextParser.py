from typing import List
from prudens_core.entities.Literal import Literal
from prudens_core.errors.SyntaxErrors import PrudensSyntaxError, EmptyContextError

class ContextParser:
    __slots__ = ("context_string")

    def __init__(self, context_string: str) -> None:
        self.context_string: str = context_string.strip()

    def parse(self) -> List[Literal]:
        literals_str: List[str] = self.context_string.split(";")
        literals: List[Literal] = []
        if len(literals_str) == 0:
            raise EmptyContextError
        for literal_str in literals_str:
            if literal_str == "":
                continue
            try:
                literal: Literal = Literal(literal_str)
            except PrudensSyntaxError as e:
                raise e
            literals.append(literal)
        return literals