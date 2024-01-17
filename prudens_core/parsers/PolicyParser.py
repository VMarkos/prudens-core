import re
from typing import Dict, List
from prudens_core.entities.Rule import Rule
from prudens_core.entities.PriorityRelation import PriorityRelation
from prudens_core.errors.SyntaxErrors import PrudensSyntaxError, KeywordNotFoundError, MissingDelimiterError, MultipleRuleNameError

class ParsedPolicy:
    __slots__ = ("rules", "priorities")

    def __init__(self, rules: Dict[str, Rule], priorities: PriorityRelation) -> None:
        self.rules: Dict[str, Rule] = rules
        self.priorities: PriorityRelation = priorities

class PolicyParser:
    __slots__ = ("policy_string")
    
    def __init__(self, policy_string: str) -> None:
        self.policy_string: str = policy_string.strip()

    def parse(self) -> ParsedPolicy:
        if not re.match(r'^@Policy', self.policy_string, flags = re.ASCII):
            raise KeywordNotFoundError("@Policy", self.policy_string)
        if not "@Priorities" in self.policy_string:
            raise KeywordNotFoundError("@Priorities", self.policy_string)
        priorities_index: int = self.policy_string.index("@Priorities")
        main_content: str = self.policy_string[7:priorities_index].strip()
        priority_content: str = self.policy_string[priorities_index + 11:].strip()
        try:
            rules: Dict[str, Rule] = self.__parse_rules(main_content)
        except Exception as e:
            raise e
        try:
            priorities: PriorityRelation = PriorityRelation(priority_content, rules)
        except Exception as e:
            raise e
        return ParsedPolicy(rules, priorities)
        
    def __parse_rules(self, rules_string: str) -> Dict[str, Rule]:
        rules: List[str] = rules_string.split(";")
        # print(rules)
        if len(rules) == 1:
            raise MissingDelimiterError(";")
        rule_objects: Dict[str, Rule] = dict()
        for rule_str in rules:
            if rule_str == "":
                continue
            try:
                rule: Rule = Rule(rule_str)
                rule_name: str = rule.name
                if rule_name in rule_objects.keys():
                    raise MultipleRuleNameError(rule_name, rule_objects[rule_name].original_string, rule.original_string)
                rule_objects[rule_name] = rule
            except PrudensSyntaxError as e:
                raise e
        return rule_objects