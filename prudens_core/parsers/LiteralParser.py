import re
from typing import Union, List
from prudens_core.entities.Variable import Variable
from prudens_core.entities.Constant import Constant
from prudens_core.errors.SyntaxErrors import (
    InvalidArgumentError,
    PrudensSyntaxError,
    InvalidLiteralError,
)


class ParsedLiteral:
    __slots__ = ("name", "arguments", "sign", "arity", "is_external", "is_action")

    def __init__(
        self,
        name: str,
        arguments: [Union[Variable, Constant]],
        sign: bool,
        arity: int,
        is_external: bool,
        is_action: bool,
    ) -> None:
        self.name: str = name
        self.arguments: List[Union[Variable, Constant]] = arguments
        self.sign: bool = sign
        self.arity: int = arity
        self.is_external: bool = is_external
        self.is_action: bool = is_action


class LiteralParser:
    __slots__ = "literal_string"

    def __init__(self, literal_string: str) -> None:
        self.literal_string: str = literal_string.strip()

    def parse(self) -> ParsedLiteral:
        # print("LiteralParser:", self.literal_string)
        is_propositional: bool = re.fullmatch(
            r"-?(\?|!)?[a-z]\w*", self.literal_string, flags=re.ASCII
        )
        if is_propositional:
            sign: bool = self.literal_string[0] != "-"
            is_external: bool = (
                sign
                and self.literal_string[0] == "?"
                or not sign
                and self.literal_string[1] == "?"
            )
            is_action: bool = (
                sign
                and self.literal_string[0] == "!"
                or not sign
                and self.literal_string[1] == "!"
            )
            name: str = self.literal_string if sign else self.literal_string[1:]
            return ParsedLiteral(name, [], sign, 0, is_external, is_action)
        is_fol: bool = re.fullmatch(
            r"-?(\?|!)?[a-z]\w*\s*\(.+\)", self.literal_string, flags=re.ASCII
        )
        if is_fol:
            sign: bool = self.literal_string[0] != "-"
            is_external: bool = (
                sign
                and self.literal_string[0] == "?"
                or not sign
                and self.literal_string[1] == "?"
            )
            is_action: bool = (
                sign
                and self.literal_string[0] == "!"
                or not sign
                and self.literal_string[1] == "!"
            )
            paren_pos: int = self.literal_string.find("(")
            name: str = (
                self.literal_string[:paren_pos]
                if sign
                else self.literal_string[1:paren_pos]
            )
            arguments_string: str = self.literal_string[paren_pos + 1 : -1]
            valid_arg_regexp: str = r"^[a-zA-Z0-9]\w*"
            predicate_arguments: [Union[Variable, Constant]] = []
            for arg in arguments_string.split(","):
                arg = arg.strip()
                is_valid_arg: bool = re.fullmatch(valid_arg_regexp, arg)
                if not is_valid_arg:
                    raise InvalidArgumentError("Error in predicate " + name, arg)
                if re.match(
                    r"[a-z0-9]", arg[0]
                ):  # FIXME This ignores cases such as `1 + X`.
                    try:
                        arg_obj: Constant = Constant(arg)
                    except PrudensSyntaxError as e:
                        raise e
                else:
                    try:
                        arg_obj: Variable = Variable(arg)
                    except PrudensSyntaxError as e:
                        raise e
                predicate_arguments.append(arg_obj)
            return ParsedLiteral(
                name,
                predicate_arguments,
                sign,
                len(predicate_arguments),
                is_external,
                is_action,
            )
        raise InvalidLiteralError(self.literal_string)
