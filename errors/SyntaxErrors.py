class PrudensSyntaxError(Exception):
    """Generic syntax error"""

class UnmatchedDoubleQuoteError(PrudensSyntaxError):
    """String constants should be enclosed in double quotes (")."""

    __slots__ = ("string")

    def __init__(self, string: str, *args: object) -> None:
        self.string: str = string
        super(UnmatchedDoubleQuoteError, self).__init__("Missing closing double quote (\") in " + self.string +\
                                                        ". " + self.__doc__, *args)

class IllegalCharacterError(PrudensSyntaxError):
    """Variables, constants and all legitimate names (e.g., rule or literal names) within Prudens should consist only of alphanumeric characters in the ASCII sense (a-z, A-Z, 0-9, _).
    """

    __slots__ = ("illegal_character", "expression")

    def __init__(self, illegal_character: str, expression: str, *args: object) -> None:
        self.illegal_character: str = illegal_character
        self.expression: str = expression
        super(IllegalCharacterError, self).__init__("Illegal character " + self.illegal_character +\
                                                    " in expression " + self.expression, *args)
        
class InvalidArgumentError(PrudensSyntaxError):
    """All predicate arguments should start with a lower- or capital-case letter, (a-z or A-Z)."""

    __slots__ = ("message", "argument")

    def __init__(self, message: str, argument: str, *args: object) -> None:
        self.message: str = message
        self.argument: str = argument
        super(InvalidArgumentError, self).__init__(self.message + ". Invalid starting character in argument: " + self.argument +\
                                                   ". " + self.__doc__, *args)
        
class InvalidLiteralError(PrudensSyntaxError):
    """Literals should either be propositional, i.e., start with a lower case letter followed by any ASCII alphanumeric character, or first-order, i.e., as above, followed by a comma-separated list of variables or constants enclosed in parentheses. Also, literals may start with a dash (-), indicating negation, possibly followed by one of the special characters ? or !, which indicate procedural and action literals, respectively."""
    
    __slots__ = ("name")

    def __init__(self, name: str, *args: object) -> None:
        self.name: str = name
        super(InvalidLiteralError, self).__init__("Invalid syntax in literal " + self.name + ". " + self.__doc__, *args)

class InvalidRuleNameError(PrudensSyntaxError):
    """Rule names should start with a lower- or capital-case letter (a-z or A-Z) and optionally be followed by any ASCII alphanumeric character. Also, a rule's name should be separated by the rest of the rule by double double-dots (::)."""

    __slots__ = ("rule_string")

    def __init__(self, rule_string: str, *args: object) -> None:
        self.rule_string: str = rule_string
        super(InvalidRuleNameError, self).__init__("Invalid rule name in\n" + self.rule_string + "\n" +\
                                                   self.__doc__, *args)
        
class MultipleKeywordError(PrudensSyntaxError):
    """Some keywords, such as 'implies', '::', and '@Policy' should appear exactly once throughout their enclosing entity (rules in the first two cases and policies in the last one). Consider also having missed some delimiter, such as ';' at the end of each rule."""
    
    __slots__ = ("keyword", "rule_string")
    
    def __init__(self, keyword: str, rule_string: str, *args: object) -> None:
        self.keyword: str = keyword
        self.rule_string: str = rule_string
        super(MultipleKeywordError, self).__init__("More than one '" + self.keyword + "' found in:\n" +\
                                                            self.rule_string + "\n" + self.__doc__, *args)
        
class KeywordNotFoundError(PrudensSyntaxError):
    """For instance, you might have missed 'implies' from a rule declaration or '@Policy' from the begining of your policy."""
    
    __slots__ = ("keyword", "code_string")
    
    def __init__(self, keyword: str, code_string: str, *args: object) -> None:
        self.keyword: str = keyword
        self.code_string: str = code_string
        super(KeywordNotFoundError, self).__init__("Keyword " + self.keyword + " not found in:\n" +\
                                                   self.code_string + "\n" + self.__doc__, *args)
        
class MissingDelimiterError(PrudensSyntaxError):
    """For instance, you might have missed ';' at the end of some rule(s)."""
    
    __slots__ = ("delim")
    
    def __init__(self, delim: str, *args: object) -> None:
        self.delim: str = delim
        super(MissingDelimiterError, self).__init__("Delimiter " + self.delim + " not found. " +\
                                                    self.__doc__, *args)
        
class MultipleDelimiterError(PrudensSyntaxError):
    """For instance, you might have added double ';' at the end of some rule(s)."""
    
    __slots__ = ("delim")
    
    def __init__(self, delim: str, *args: object) -> None:
        self.delim: str = delim
        super(MultipleDelimiterError, self).__init__("Delimiter " + self.delim + " found more than once." +\
                                                     self.__doc__, *args)
        
class MultipleRuleNameError(PrudensSyntaxError):
    """Different rules in the same policy should have different names, as a rule's name is used in uniquely identifying it."""
    
    __slots__ = ("duplicate_name", "rule_string_1", "rule_string_2")
    
    def __init__(self, name: str, r1: str, r2: str, *args: object) -> None:
        self.duplicate_name: str = name
        self.rule_string_1: str = r1
        self.rule_string_2: str = r2
        super(MultipleRuleNameError, self).__init__("Rules " + self.rule_string_1 + " and " +\
                                                    self.rule_string_2 + " have the same name: " +\
                                                    self.duplicate_name + ". " + self.__doc__, *args)
        
class MalformedPriorityError(PrudensSyntaxError):
    """A rule priority should start with the highest priority rule's name, followed by '>' and then by the lowest priority rule's name, potentially separated by whitespace."""
    
    __slots__ = ("priority")
    
    def __init__(self, priority: str, *args: object) -> None:
        self.priority: str = priority
        super(MalformedPriorityError, self).__init__("Malformed priority " + self.priority +\
                                                     ". " + self.__doc__, *args)
        
class EmptyContextError(PrudensSyntaxError):
    """A context should contain at least one literal."""
    def __init__(self, *args) -> None:
        super(EmptyContextError, self).__init__("Empty context. " + self.__doc__, *args)

class EmptyRuleBodyError(PrudensSyntaxError):
    """A rule should have a non-empty body."""

    __slots__ = ("rule_name")

    def __init__(self, rule_name: str, *args: object) -> None:
        self.rule_name: str = rule_name
        super(EmptyRuleBodyError, self).__init__(f"Empty rule body for rule {self.rule_name}. "\
                                                 + self.__doc__, *args)
        
class ReferenceError(PrudensSyntaxError):
    """A referenced Prudens entity does not exist. For instance, you might have referenced a rule that does not exist or have forgotten a delimiter such as a ';' or a '::'."""

    __slots__ = ("entity_str")

    def __init__(self, entity_str: str, *args: object) -> None:
        self.entity_str: str = entity_str
        super(ReferenceError, self).__init__(f"Entity {entity_str} referenced but\
                                             it does not exist. " + self.__doc__, *args)