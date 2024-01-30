from __future__ import annotations
from typing import Union, Dict, List
from prudens_core.entities.Variable import Variable
from prudens_core.entities.Constant import Constant
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.LiteralParser import LiteralParser, ParsedLiteral
from prudens_core.errors.RuntimeErrors import DuplicateValueError
import prudens_core.utilities.utils as utils


class Literal:
    __slots__ = (
        "original_string",
        "_name",
        "_sign",
        "_arity",
        "arguments",
        "_is_external",
        "_is_action",
        "signature",
    )

    def __init__(self, literal_string: str = None) -> None:
        if literal_string:
            self.original_string: str = literal_string
            parser: LiteralParser = LiteralParser(self.original_string)
            try:
                parsed_literal: ParsedLiteral = parser.parse()
            except Exception as e:
                raise e
            self._name: str = parsed_literal.name
            self._sign: bool = parsed_literal.sign
            self._arity: int = parsed_literal.arity
            self.arguments: List[Union[Variable, Constant]] = parsed_literal.arguments
            self._is_external: bool = (
                parsed_literal.is_external
            )  # TODO Don't you need at this point a field for the code or the code reference?
            self._is_action: bool = parsed_literal.is_action
            self.signature: str = self.__get_signature()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if new_name != self._name:
            self._name = new_name
            self.signature = self.__get_signature()

    @property
    def sign(self) -> bool:
        return self._sign

    @sign.setter
    def sign(self, new_sign: bool) -> None:
        if new_sign != self._sign:
            self._sign = new_sign
            self.signature = self.__get_signature()

    @property
    def arity(self) -> int:
        return self._arity

    @arity.setter
    def arity(self, new_arity: int) -> None:
        if new_arity != self._arity:
            self._arity = new_arity
            self.signature = self.__get_signature()

    @property
    def is_external(self) -> bool:
        return self._is_external

    @is_external.setter
    def is_external(self, new_is_external: bool) -> None:
        if new_is_external != self._is_external:
            self.is_external = new_is_external
            self.signature = self.__get_signature()

    @property
    def is_action(self) -> bool:
        return self._is_action

    @is_action.setter
    def is_action(self, new_is_action: bool) -> None:
        if new_is_action != self._is_external:
            self.is_external = new_is_action
            self.signature = self.__get_signature()

    @classmethod
    def from_dict(cls, init_dict: Dict) -> Literal:
        literal = cls.__new__(cls)
        literal.original_string = utils.parse_dict_prop(
            init_dict,
            "original_string",
            "Literal",
            default_value="",
            expected_types=[str],
        )
        literal._name = utils.parse_dict_prop(
            init_dict, "name", "Literal", expected_types=[str]
        )
        literal._sign = utils.parse_dict_prop(
            init_dict, "sign", "Literal", expected_types=[bool]
        )
        literal._arity = utils.parse_dict_prop(
            init_dict, "arity", "Literal", expected_types=[int]
        )
        literal._is_external = utils.parse_dict_prop(
            init_dict, "is_external", "Literal", expected_types=[bool]
        )
        literal._is_action = utils.parse_dict_prop(
            init_dict, "is_action", "Literal", expected_types=[bool]
        )
        literal.signature = utils.parse_dict_prop(
            init_dict,
            "signature",
            "Literal",
            default_value=literal.__get_signature(),
            expected_types=[str],
        )
        try:
            args_list: List[Union[Variable, Constant]] = init_dict["arguments"]
        except KeyError:
            raise KeyError(
                f"Missing key 'arguments' in {Literal} initialization from dict."
            )
        literal.arguments = []
        for i, argument in enumerate(args_list):
            var_exception = None
            try:
                lit_arg = Variable.from_dict(argument)
            except Exception as e:
                var_exception = e
            if var_exception:
                try:
                    lit_arg = Constant.from_dict(argument)
                except Exception as e:
                    raise ValueError(
                        f"Invalid literal argument in initialization of literal {literal.name} at index {i}: {argument}."
                    )
            literal.arguments.append(lit_arg)
        return literal

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "name": self._name,
            "sign": self._sign,
            "arity": self._arity,
            "arguments": [x.to_dict() for x in self.arguments],
            "is_external": self._is_external,
            "is_action": self._is_action,
            "signature": self.signature,
        }

    def is_propositional(self) -> bool:
        return self.arity == 0

    def is_truism(self) -> bool:
        return self.signature == "true0"  # FIXME What about "not true", i.e. "-true"?

    def unify(self, other: Literal) -> Union[None, Substitution]:
        if (
            self.name != other.name
            or self.sign != other.sign
            or self.arity != other.arity
            or self.is_external != other.is_external
            or self.is_action != other.is_action
            or len(self.arguments) != len(other.arguments)
        ):
            return None  # Failed to unify
        # print("Non-trivial case of literal unification!")
        # print("\tself:", self, "other:", other)
        sub = Substitution()
        if self.arity == 0:
            return sub  # Propositional literal, i.e. nothing in sub.
        for this_arg, other_arg in zip(self.arguments, other.arguments):
            # print("\tthis arg:", this_arg)
            # print("\tother arg:", other_arg)
            if not this_arg.unifies(other_arg):
                # print("\tnon-unifiable")
                return None
            if isinstance(this_arg, Variable):
                # print('extend self var by const or var')
                # print(f"self: {self.__str__()}, other: {other}, this_arg: {this_arg}, other_arg: {other_arg}")
                try:
                    sub.extend((this_arg, other_arg))
                except DuplicateValueError:
                    # print(f"Duplicate Value Error --> non-unifiable!")
                    return None
            elif isinstance(other_arg, Variable):
                # print('extend other var by const or var')
                sub.extend((other_arg, this_arg))
            # print(f"\tsub: {sub}")
        return sub

    def unifies(self, other: Literal) -> bool:
        """To be used instead of `self.unifies()` in cases where the substitution is not needed."""
        if (
            self.name != other.name
            or self.sign != other.sign
            or self.arity != other.arity
            or self.is_external != other.is_external
            or self.is_action != other.is_action
            or len(self.arguments) != len(other.arguments)
        ):
            return False
        for this_arg, other_arg in zip(self.arguments, other.arguments):
            if not this_arg.unifies(other_arg):
                return False
        return True

    def is_conflicting_with(self, other: Literal) -> bool:
        if self.sign == other.sign:
            return False
        other.sign = not other.sign
        are_equal: bool = self.unifies(other)
        other.sign = not other.sign
        return are_equal

    def __get_signature(self) -> str:
        signature: str = "" if self.sign else "-"
        signature += "?" if self.is_external else ""
        signature += "!" if self.is_action else ""
        signature += self.name
        signature += str(self.arity)
        return signature

    def __eq__(self, other: Literal) -> bool:
        # # print(self, other)
        # # print("literal equals enter")
        if not isinstance(other, Literal):
            return False
        # # print("is instance of literal")
        # return hash(self) == hash(other)
        if self.signature != other.signature:
            return False
        # # print("same signature")
        self_var_indices: Dict[Variable, int] = dict()
        other_var_indices: Dict[Variable, int] = dict()
        # # print("arity:", self.arity)
        for i, (self_arg, other_arg) in enumerate(zip(self.arguments, other.arguments)):
            if (isinstance(self_arg, Constant) and isinstance(other_arg, Variable)) or (
                isinstance(self_arg, Variable) and isinstance(other_arg, Constant)
            ):
                return False
            if isinstance(self_arg, Constant) and not self_arg == other_arg:
                return False
            try:
                self_index: int = self_var_indices[self_arg]
            except KeyError:
                self_index: int = i
                self_var_indices[self_arg] = i
            try:
                other_index: int = other_var_indices[other_arg]
            except KeyError:
                other_index: int = i
                other_var_indices[other_arg] = i
            if self_index != other_index:
                return False
        return True

    def __hash__(self) -> int:
        h = 2166136261
        h = (h * 16777619) ^ hash(self._sign)
        h = (h * 16777619) ^ hash(self._name)
        h = (h * 16777619) ^ hash(self._arity)
        h = (h * 16777619) ^ hash(self._is_action)
        h = (h * 16777619) ^ hash(self._is_external)
        for _arg in self.arguments:
            h = (h * 16777619) ^ hash(_arg)
        return h

    # def __hash__(self) -> int:
    #     hash_str: str = self.signature
    #     variable_indices: Dict[str, int] = dict()
    #     for i, arg in enumerate(self.arguments):
    #         if isinstance(arg, Constant):
    #             hash_str += "." + str(arg)
    #         else:
    #             var_name: str = str(arg)
    #             try:
    #                 hash_str += "." + str(variable_indices[var_name])
    #             except KeyError:
    #                 hash_str += "." + str(i)
    #                 variable_indices[var_name] = i
    #     return hash(hash_str)

    def __deepcopy__(self, memodict={}) -> Literal:
        copycat: Literal = Literal()
        copycat.original_string = self.original_string
        copycat._name = self._name
        copycat._sign = self._sign
        copycat._arity = self._arity
        copycat.arguments = self.arguments[:]
        copycat._is_external = self._is_external
        copycat._is_action = self._is_action
        copycat.signature = self.signature
        return copycat

    def __str__(self) -> str:
        literal_str: str = "" if self.sign else "-"
        literal_str += "?" if self.is_external else ""
        literal_str += "!" if self.is_action else ""
        literal_str += self.name
        if self.is_propositional():
            return literal_str
        literal_str += "(" + str(self.arguments[0])
        for argument in self.arguments[1:]:
            literal_str += ", " + str(argument)
        return literal_str + ")"
