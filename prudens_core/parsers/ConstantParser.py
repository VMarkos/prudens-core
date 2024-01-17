import re
from typing import Union
from enum import Enum
from prudens_core.errors.SyntaxErrors import UnmatchedDoubleQuoteError, InvalidArgumentError

class ConstantType(Enum):
    INT = 1
    FLOAT = 2
    STRING = 3
    ENTITY = 4

class ParsedConstant:
    __slots__ = ("value", "type")

    def __init__(self, value: Union[int, str, float], type: ConstantType):
        self.value: Union[int, str, float] = value
        self.type: ConstantType = type

class ConstantParser:
    __slots__ = ("constant_string")

    def __init__(self, constant_string: str) -> None:
        self.constant_string: str = constant_string.strip()

    def parse(self) -> ParsedConstant:
        is_int: bool = False
        try:
            dummy_int: int = int(self.constant_string)
            is_int = True
        except ValueError:
            pass
        if is_int:
            return self.parse_int()
        is_float: bool = False
        try:
            dummy_float: float = float(self.constant_string)
            is_float = True
        except ValueError:
            pass
        if is_float:
            return self.parse_float()
        if self.constant_string[0] in ['"', '\'']:
            return self.parse_string()
        return self.parse_entity()
    
    def parse_string(self) -> ParsedConstant:
        if self.constant_string[-1] not in ['"', '\'']:
            raise UnmatchedDoubleQuoteError(self.constant_string)
        return ParsedConstant(self.constant_string[1:-1], ConstantType.STRING)
    
    def parse_entity(self) -> ParsedConstant:
        if not re.fullmatch(r'[a-z]\w*', self.constant_string, flags = re.ASCII):
            raise InvalidArgumentError("Syntax error in constant ", self.constant_string)
        return ParsedConstant(self.constant_string, ConstantType.ENTITY)

    def parse_float(self) -> ParsedConstant:
        return ParsedConstant(float(self.constant_string), ConstantType.FLOAT)

    def parse_int(self) -> ParsedConstant:
        return ParsedConstant(int(self.constant_string), ConstantType.INT)