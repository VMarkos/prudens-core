import re
from typing import List, Dict
import numpy as np
from numpy.typing import ArrayLike
from scipy.sparse import dok_matrix
from prudens_core.entities.Rule import Rule
from prudens_core.errors.SyntaxErrors import MissingDelimiterError, MalformedPriorityError, ReferenceError

class ParsedPriorityRelation:
    __slots__ = ("rule_indices", "priorities", "conflict_matrix", "default")

    def __init__(self, rule_indices: Dict[str, int], priorities: dok_matrix, conflict_matrix: dok_matrix, default: bool = False) -> None:
        self.rule_indices: Dict[str, int] = rule_indices
        self.priorities: dok_matrix = priorities
        self.conflict_matrix: dok_matrix = conflict_matrix
        self.default: bool = default

class PriorityRelationParser: # FIXME Check that all names appearing in priorities are also part of the policy!
    __slots__ = ("priority_str", "rules")

    def __init__(self, priority_str: str, rules: Dict[str, Rule]) -> None:
        self.priority_str: str = priority_str.strip()
        self.rules = rules

    def parse(self) -> ParsedPriorityRelation:
        n: int = len(self.rules)
        priority_matrix: ArrayLike = np.zeros((n, n), dtype = int)
        rule_names: List[str] = list(self.rules.keys())
        rule_indices: Dict[str, int] = { rule_names[i]: i for i in range(n) }
        conflict_matrix: dok_matrix = self.__generate_conflict_matrix(rule_names)
        if self.priority_str == "default":
            default_priorities: dok_matrix = self.__generate_default_priorities(rule_names)
            return ParsedPriorityRelation(rule_indices, default_priorities, conflict_matrix, default = True)
        priorities: List[str] = self.priority_str.split(";")
        if len(priorities) == 1:
            raise MissingDelimiterError(";")
        for priority in priorities:
            if priority == "":
                continue
            try:
                parsed_priority: List[str] = self.__parse_priority_str(priority.strip())
            except MalformedPriorityError as e:
                raise e
            try:
                higher: Rule = self.rules[parsed_priority[0]]
            except KeyError:
                raise ReferenceError(parsed_priority[0])
            try:
                lower: Rule = self.rules[parsed_priority[1]]
            except KeyError:
                raise ReferenceError(parsed_priority[1])
            # print\("rules:", higher, lower)
            if higher.is_conflicting_with(lower):
                # print\("conflict")
                priority_matrix[rule_indices[parsed_priority[0]]][rule_indices[parsed_priority[1]]] = 1
        # print\(priority_matrix)
        return ParsedPriorityRelation(rule_indices, dok_matrix(priority_matrix), conflict_matrix)
    
    def __generate_conflict_matrix(self, rule_names) -> dok_matrix:
        n: int = len(self.rules)
        conflict_matrix: ArrayLike = np.zeros((n, n), dtype = int)
        for i in range(n):
            row_rule: Rule = self.rules[rule_names[i]]
            for j in range(n):
                if i == j:
                    continue
                col_rule: Rule = self.rules[rule_names[j]]
                if row_rule.is_conflicting_with(col_rule):
                    conflict_matrix[i][j] = 1
        return dok_matrix(conflict_matrix)

    def __generate_default_priorities(self, rule_names) -> dok_matrix:
        n: int = len(self.rules)
        priority_matrix: ArrayLike = np.zeros((n, n), dtype = int)
        for i in range(n - 1):
            row_rule: Rule = self.rules[rule_names[i]]
            for j in range(i + 1, n):
                col_rule: Rule = self.rules[rule_names[j]]
                if row_rule.is_conflicting_with(col_rule):
                    priority_matrix[j][i] = 1
        return dok_matrix(priority_matrix)

    def __parse_priority_str(self, priority_string: str) -> List[str]:
        if not re.match(r'^[a-zA-Z]\w*\s*\>\s*[a-zA-Z]\w*', priority_string, flags = re.ASCII):
            raise MalformedPriorityError(priority_string)
        return [x.strip() for x in priority_string.split(">") if x]