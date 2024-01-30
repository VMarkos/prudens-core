import re
from enum import Enum
from types import CodeType
from typing import Union

# import parser
from prudens_core.errors.SyntaxErrors import IllegalCharacterError


class VariableType(Enum):
    VARIABLE = 1
    EXPRESSION = 2


class ParsedVariable:
    __slots__ = ("name", "type", "code")

    def __init__(self, name: str, type: VariableType, code: CodeType) -> None:
        self.name: str = name
        self.type: VariableType = type
        self.code: Union[None, CodeType] = code


class VariableParser:
    __slots__ = "variable_string"

    def __init__(self, variable_string: str) -> None:
        self.variable_string: str = variable_string.strip()

    def parse(self) -> ParsedVariable:
        if re.fullmatch(r"[A-Z]\w*", self.variable_string, flags=re.ASCII):
            return self.parse_variable()
        return self.parse_expression()

    def parse_variable(self) -> ParsedVariable:
        return ParsedVariable(self.variable_string, VariableType.VARIABLE, None)

    def parse_expression(self) -> ParsedVariable:
        is_not_math: str = (
            r"[^\d\+\-\*\^/,\(\)\%]+"  # TODO This might need to be revisited.
        )
        illegal_char: re.Match = re.search(is_not_math, self.variable_string)
        if illegal_char:
            raise IllegalCharacterError(illegal_char[0], self.variable_string)
        # FIXME This has to be made python 3.13 compatible!
        # try:
        #     st = parser.expr(self.variable_string)
        # except SyntaxError as e: # FIXME How do you handle the rest exceptions?
        #     raise e
        code: CodeType = st.compile()
        return ParsedVariable("", VariableType.EXPRESSION, code)
