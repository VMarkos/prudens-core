from __future__ import annotations
from typing import Union, TYPE_CHECKING
from types import CodeType
# import parser
# import copy
from prudens_core.entities.Constant import Constant
if TYPE_CHECKING:
    from prudens_core.entities.Substitution import Substitution
    from prudens_core.errors.RuntimeErrors import InvalidEvaluationError, UnassignedVariableError, MalformedExpressionError
from prudens_core.parsers.VariableParser import VariableParser, ParsedVariable, VariableType
from prudens_core.errors.SyntaxErrors import PrudensSyntaxError

class Variable: # TODO Consider adding fields about the (rule), literal and position of the variable.
    __slots__ = ("original_string", "is_assigned", "value", "name", "type", "code")

    def __init__(self, variable_string: str) -> None:
        parser: VariableParser = VariableParser(variable_string)
        try:
            parsed_variable: ParsedVariable = parser.parse()
        except Exception as e:
            raise e
        self.original_string: str = variable_string
        self.is_assigned: bool  = False # FIXME Since Variables are substituted by Constants, is this needed? Essentially, Variables ARE PLACEHOLDERS, so this should not be needed!
        self.value: Union[None, Constant] = None
        self.name: str = parsed_variable.name
        self.type: VariableType = parsed_variable.type
        self.code: Union[None, CodeType] = parsed_variable.code

    def unifies(self, other: Union[Variable, Constant]) -> bool:
        if isinstance(other, Variable):
            return self.type == VariableType.VARIABLE and other.type == VariableType.VARIABLE\
                and (not self.is_assigned or not other.is_assigned or\
                (self.value and self.value.unifies(other.value)))
        return not self.is_assigned
    
    def assign(self, value: Union[None, Constant]): # Assigning `None` to a variable de-assigns it.
        self.is_assigned = value != None
        self.value = value

    def evaluate(self, sub: Substitution) -> None:
        if self.type == VariableType.VARIABLE:
            raise InvalidEvaluationError
        _preamble = sub.to_code()
        exec(_preamble)
        try:
            evaluated_code = eval(self.code) # FIXME Beware of single quotes!
        except NameError as e:
            raise UnassignedVariableError(e.name)
        try:
            self.value = Constant(evaluated_code)
        except PrudensSyntaxError as e:
            raise MalformedExpressionError(str(e), self.original_string)

    def __str__(self) -> str:
        if self.type == VariableType.EXPRESSION:
            return str(self.code)
        return self.name
    
    def __eq__(self, other: Variable) -> bool:
        if not isinstance(other, Variable):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)