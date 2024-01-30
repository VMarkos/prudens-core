from __future__ import annotations
from typing import List, TYPE_CHECKING, FrozenSet
from prudens_core.entities.Variable import Variable
from prudens_core.entities.Constant import Constant

if TYPE_CHECKING:
    from prudens_core.entities.Literal import Literal


class PrudensRuntimeError(Exception):
    """Generic runtime error"""


class MissingVariableError(PrudensRuntimeError):
    """Missing variable in substitution"""

    __slots__ = "variable"

    def __init__(self, variable: Variable, *args: object) -> None:
        self.variable: Variable = variable
        super(MissingVariableError, self).__init__(
            "Missing variable " + str(self.variable) + " in substitution.", *args
        )


class InvalidEvaluationError(PrudensRuntimeError):
    """Erroneous attempt to evaluate variable that does not correspond to expression"""

    __slots__ = "variable"

    def __init__(self, variable: Variable, *args: object) -> None:
        self.variable: Variable = variable
        super(InvalidEvaluationError, self).__init__(
            "Erroneous attempt to evaluate variable "
            + str(self.variable)
            + " that does not correspond to expression",
            *args,
        )


class UnassignedVariableError(PrudensRuntimeError):
    """Erroneous attempt to evaluate variable that does not exist or has not been unified with some constant so far."""

    def __init__(self, name: str, *args: object) -> None:
        super(UnassignedVariableError, self).__init__(
            "Variable "
            + name
            + " does not exist or has not been unified with some constant so far",
            *args,
        )


class MalformedExpressionError(PrudensRuntimeError):
    """Syntax error that was found during runtime, when compiling and evaluating expression"""

    __slots__ = "message"

    def __init__(self, message: str, expression: str, *args: object) -> None:
        self.message: str = message
        super(MalformedExpressionError, self).__init__(
            self.__doc__ + " " + expression + "\n\t" + self.message, *args
        )


class VariableNotFoundInSubstitutionError(PrudensRuntimeError):
    """Variable name not found in substitution keys"""

    def __init__(self, variable: Variable, *args: object) -> None:
        super(VariableNotFoundInSubstitutionError, self).__init__(
            "Variable " + str(variable) + " not found in substitution.", *args
        )


class DuplicateValueError(PrudensRuntimeError):
    """A variable should take a single value within the same substitution."""

    __slots__ = ("variable", "value_1", "value_2")

    def __init__(
        self, variable: Variable, value_1: Constant, value_2: Constant, *args: object
    ) -> None:
        self.variable: Variable = variable
        self.value_1: Constant = value_1
        self.value_2: Constant = value_2
        super(DuplicateValueError, self).__init__(
            "Variable "
            + str(variable)
            + " assigned with two values ("
            + str(value_1)
            + ", "
            + str(value_2)
            + ") in the same substitution. "
            + self.__doc__,
            *args,
        )


class RuleNotFoundError(PrudensRuntimeError):
    """Check again if the rule is included in the policy."""

    __slots__ = "rule_string"

    def __init__(self, rule_string: str, *args: object) -> None:
        self.rule_string: str = rule_string
        super(RuleNotFoundError, self).__init__(
            "Rule " + self.rule_string + " not found in policy. " + self.__doc__, *args
        )


class LiteralNotInContextError(PrudensRuntimeError):
    """Literal not found in context."""

    __slots__ = "literal"

    def __init__(self, literal: Literal, *args: object) -> None:
        self.literal: Literal = literal
        super(LiteralNotInContextError, self).__init__(
            "Literal " + literal.original_string + " not found in context.", *args
        )


class LiteralAlreadyInContextError(PrudensRuntimeError):
    """Literal is already included in context."""

    __slots__ = "literal"

    def __init__(self, literal: Literal, *args: object) -> None:
        self.literal: Literal = literal
        super(LiteralAlreadyInContextError, self).__init__(
            "Literal " + str(self.literal) + " already in context.", *args
        )


class UnresolvedConflictsError(PrudensRuntimeError):
    """Conflict between two rules has not been resolved by priorities."""

    __slots__ = "conflicts"

    def __init__(self, conflicts: List[FrozenSet[str, str]], *args: object) -> None:
        self.conflicts: List[FrozenSet[str, str]] = conflicts
        super(UnresolvedConflictsError, self).__init__(
            "Conflict between rules "
            + ", ".join([" and ".join(x) for x in self.conflicts])
            + " has not been resolved.",
            *args,
        )
