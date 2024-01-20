import re
from typing import List
from prudens_core.entities.Literal import Literal
from prudens_core.errors.SyntaxErrors import InvalidRuleNameError, MultipleKeywordError, KeywordNotFoundError, EmptyRuleBodyError, MissingDelimiterError

class ParsedRule:
    __slots__ = ("name", "body", "head")

    def __init__(self, name: str, body: [Literal], head: Literal) -> None:
        self.name: str = name
        self.body: [Literal] = body
        self.head: Literal = head

class RuleParser:
    __slots__ = ("rule_string")

    def __init__(self, rule_string: str) -> None:
        self.rule_string = rule_string.strip()

    def parse(self): # FIXME Reconsider whether the .+ solution to ignore sta
        rule_preamble_regex: str = r'^[a-zA-Z]\w*\s*::\s*'
        if "::" not in self.rule_string:
            raise MissingDelimiterError("::")
        if not re.match(rule_preamble_regex, self.rule_string):
            raise InvalidRuleNameError(self.rule_string) # TODO There should be some way to prohibit some reserved words from being used.
        rule_split: [str] = self.rule_string.split("::")
        rule_name: str = rule_split[0].strip()
        if len(rule_split) > 2:
            raise MultipleKeywordError("::", self.rule_string)
        main_part: str = rule_split[1]
        if "implies" not in main_part:
            raise KeywordNotFoundError("implies", self.rule_string)
        main_split: [str] = main_part.split("implies")
        if len(main_split) > 2:
            raise MultipleKeywordError("implies", self.rule_string)
        body_split: [str] = self.__rule_body_split(main_split[0]) # FIXME This needs to be specified!
        if not body_split or len(body_split) == 1 and re.fullmatch(r'\s*', body_split[0]):
            raise EmptyRuleBodyError(rule_name)
        body: List[Literal] = []
        for literal_str in body_split:
            try:
                body_literal: Literal = Literal(literal_str)
            except Exception as e: # TODO Consider being more specific here, which means that you should somehow resolve the syntax + runtime error of having unassigned variables in math expressions.
                raise e
            body.append(body_literal)
        try:
            head_literal: Literal = Literal(main_split[1])
        except Exception as e:
            raise e
        return ParsedRule(rule_name, body, head_literal)
    
    def __rule_body_split(self, rule_body_str: str, delim: str = ",") -> List[str]:
        unclosed_parentheses: int = 0
        split_array: List[str] = []
        current_part: str = ""
        for char in rule_body_str:
            if char == "(":
                unclosed_parentheses += 1
            elif char == ")":
                unclosed_parentheses -= 1
            if char == delim and unclosed_parentheses == 0:
                split_array.append(current_part)
                current_part = ""
                continue
            current_part += char
        split_array.append(current_part)
        return split_array