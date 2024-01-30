from __future__ import annotations
from typing import Union, Dict
from prudens_core.parsers.ConstantParser import (
    ConstantParser,
    ParsedConstant,
    ConstantType,
)
import prudens_core.utilities.utils as utils


class Constant:
    __slots__ = ("original_string", "value", "type")

    def __init__(self, constant_string: str) -> None:
        parser: ConstantParser = ConstantParser(constant_string)
        try:
            parsed_constant: ParsedConstant = parser.parse()
        except Exception as e:  # TODO Complete this
            raise e
        self.original_string: str = constant_string
        self.value: Union[int, float, str] = parsed_constant.value
        self.type: ConstantType = parsed_constant.type

    @classmethod
    def from_dict(cls, init_dict: dict) -> Constant:
        constant = cls.__new__(cls)
        constant.original_string = utils.parse_dict_prop(
            init_dict,
            "original_string",
            "Constant",
            default_value="",
            expected_types=[str],
        )
        constant.value = utils.parse_dict_prop(
            init_dict, "value", "Constant", expected_types=[int, float, str]
        )
        try:
            constant_type = init_dict["type"]
        except KeyError:
            raise KeyError("Missing key 'type' in Constant initialization from dict.")
        try:
            constant.type = ConstantType[constant_type]
        except KeyError:
            raise KeyError(
                f"Wrong constant type provided: '{constant_type}'. Accepted types: {[x.name for x in ConstantType]}."
            )
        return constant

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "value": self.value,
            "type": self.type.name,
        }

    def unifies(self, other: Union[Constant, "Variable"]) -> bool:
        if isinstance(other, Constant):
            return self.value == other.value and self.type == other.type
        return True  # FIXME You have to somehow manage cyclic references (Constants <-> Variables).

    def __eq__(self, other: Constant) -> bool:
        if not isinstance(other, Constant):
            return False
        return self.type == other.type and self.value == other.value

    def __str__(self) -> str:
        if self.type == ConstantType.INT or self.type == ConstantType.FLOAT:
            return str(self.value)
        if self.type == ConstantType.STRING:
            return '"' + self.value + '"'
        return self.value

    # TODO Consider redefining __eq__ and __hash__ as in Variable class.
