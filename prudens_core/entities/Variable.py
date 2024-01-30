from __future__ import annotations
from typing import Union, Dict, TYPE_CHECKING
from types import CodeType

# import parser
# import copy
from prudens_core.entities.Constant import Constant

if TYPE_CHECKING:
    from prudens_core.entities.Substitution import Substitution
    from prudens_core.errors.RuntimeErrors import (
        InvalidEvaluationError,
        UnassignedVariableError,
        MalformedExpressionError,
    )
from prudens_core.parsers.VariableParser import (
    VariableParser,
    ParsedVariable,
    VariableType,
)
from prudens_core.errors.SyntaxErrors import PrudensSyntaxError
import prudens_core.utilities.utils as utils


class Variable:  # TODO Consider adding fields about the (rule), literal and position of the variable.
    __slots__ = ("original_string", "name", "type", "code")

    def __init__(self, variable_string: str) -> None:
        parser: VariableParser = VariableParser(variable_string)
        try:
            parsed_variable: ParsedVariable = parser.parse()
        except Exception as e:
            raise e
        self.original_string: str = variable_string
        self.name: str = parsed_variable.name
        self.type: VariableType = parsed_variable.type
        self.code: Union[None, CodeType] = parsed_variable.code

    @classmethod
    def from_dict(cls, init_dict: Dict) -> Variable:
        variable = cls.__new__(cls)
        variable.original_string = utils.parse_dict_prop(
            init_dict,
            "original_string",
            "Variable",
            default_value="",
            expected_types=[str],
        )
        variable.name = utils.parse_dict_prop(
            init_dict, "name", "Variable", expected_types=[str]
        )
        variable.code = utils.parse_dict_prop(
            init_dict,
            "code",
            "Variable",
            default_value=None,
            expected_types=[type(None), CodeType],
        )
        try:
            var_type = init_dict["type"]
        except KeyError:
            raise KeyError("Missing key 'type' in Variable initialization from dict.")
        try:
            variable.type = VariableType[var_type]
        except KeyError:
            raise KeyError(
                f"Wrong variable type provided: '{var_type}'. Accepted types: {[x.name for x in VariableType]}."
            )
        return variable

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "name": self.name,
            "type": self.type.name,
            "code": self.code,
        }

    def unifies(self, other: Union[Variable, Constant]) -> bool:
        if isinstance(other, Variable):
            return (
                self.type == VariableType.VARIABLE
                and other.type == VariableType.VARIABLE
            )
        return True

    # def assign(self, value: Union[None, Constant]): # Assigning `None` to a variable de-assigns it.
    #     self.is_assigned = value != None
    #     self.value = value

    def evaluate(self, sub: Substitution) -> None:
        if self.type == VariableType.VARIABLE:
            raise InvalidEvaluationError
        _preamble = sub.to_code()
        exec(_preamble)
        try:
            evaluated_code = eval(self.code)  # FIXME Beware of single quotes!
        except NameError as e:
            raise UnassignedVariableError(e.name)
        # try:
        #     self.value = Constant(evaluated_code)
        # except PrudensSyntaxError as e:
        #     raise MalformedExpressionError(str(e), self.original_string)

    def __str__(self) -> str:
        if self.type == VariableType.EXPRESSION:
            return str(self.code)
        return self.name

    def __eq__(self, other: Variable) -> bool:
        if not isinstance(other, Variable):
            return False
        return True  # self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
