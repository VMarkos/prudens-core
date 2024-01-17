from __future__ import annotations
from typing import Union, Dict
from prudens_core.entities.Variable import Variable
from prudens_core.entities.Constant import Constant
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.LiteralParser import LiteralParser, ParsedLiteral
from prudens_core.errors.RuntimeErrors import DuplicateValueError

class Literal:
    __slots__ = ("original_string", "_name", "_sign", "_arity", "arguments", "_is_external", "_is_action",
                 "signature")

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
            self.arguments: Union[Variable, Constant] = parsed_literal.arguments
            self._is_external: bool = parsed_literal.is_external # TODO Don't you need at this point a field for the code or the code reference?
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

    def is_propositional(self) -> bool:
        return self.arity == 0
    
    def is_truism(self) -> bool:
        return self.signature == "true0" # FIXME What about "not true", i.e. "-true"?
    
    def unify(self, other: Literal) -> Union[None, Substitution]:
        if self.name != other.name or self.sign != other.sign or self.arity != other.arity or\
           self.is_external != other.is_external or self.is_action != other.is_action or\
            len(self.arguments) != len(other.arguments):
            return None # Failed to unify
        # print("Non-trivial case of literal unification!")
        # print("\tself:", self, "other:", other)
        sub = Substitution()        
        if self.arity == 0:
            return sub # Propositional literal, i.e. nothing in sub.
        for i in range(len(self.arguments)):
            this_arg: Union[Variable, Constant] = self.arguments[i]
            other_arg: Union[Variable, Constant] = other.arguments[i]
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
    
    def is_conflicting_with(self, other: Literal) -> bool:
        if self.sign == other.sign:
            return False
        other.sign = not other.sign
        are_equal: bool = bool(self.unify(other))
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
        if self.signature != other.signature:
            return False
        # # print("same signature")
        self_var_indices: Dict[str, int] = dict()
        other_var_indices: Dict[str, int] = dict()
        # # print("arity:", self.arity)
        for i in range(self.arity):
            self_arg: Union[Variable, Constant] = self.arguments[i]
            other_arg: Union[Variable, Constant] = other.arguments[i]
            if (isinstance(self_arg, Constant) and isinstance(other_arg, Variable)) or (isinstance(self_arg, Variable) and isinstance(other_arg, Constant)):
                return False
            if isinstance(self_arg, Constant) and not self_arg == other_arg:
                return False
            self_var: str = str(self_arg)
            other_var: str = str(other_arg)
            try:
                self_index: int = self_var_indices[self_var]
            except KeyError:
                self_index: int = i
                self_var_indices[self_var] = i
            try:
                other_index: int = other_var_indices[other_var]
            except KeyError:
                other_index: int = i
                other_var_indices[other_var] = i
            if self_index != other_index:
                return False
        return True

    def __hash__(self) -> int:
        hash_str: str = self.signature
        variable_indices: Dict[str, int] = dict()
        for i in range(self.arity):
            arg: Union[Variable, Constant] = self.arguments[i]
            if isinstance(arg, Constant):
                hash_str += "." + str(arg)
            else:
                var_name: str = str(arg)
                try:
                    hash_str += "." + str(variable_indices[var_name])
                except KeyError:
                    hash_str += "." + str(i)
                    variable_indices[var_name] = i
        return hash(hash_str)

    def __deepcopy__(self, memodict = {}) -> Literal:
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