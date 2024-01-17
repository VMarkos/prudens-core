from typing import Dict, Set, List, FrozenSet
from scipy.sparse import dok_matrix
from prudens_core.entities.Literal import Literal
from prudens_core.entities.Rule import Rule
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.PriorityRelationParser import PriorityRelationParser, ParsedPriorityRelation
from prudens_core.errors.RuntimeErrors import UnresolvedConflictsError

class PriorityRelation:
    __slots__ = ("original_string", "rule_heads", "rule_indices", "indice_rules", "priorities",
                 "conflict_matrix", "default")

    def __init__(self, priority_str: str, rules: Dict[str, Rule]) -> None:
        self.original_string: str = priority_str
        parser: PriorityRelationParser = PriorityRelationParser(self.original_string, rules)
        try:
            parsed_priorities: ParsedPriorityRelation = parser.parse()
        except Exception as e:
            raise e
        self.rule_heads: Dict[str, Literal] = { rule_name: rule.head for rule_name, rule in rules.items() }
        self.rule_indices: Dict[str, int] = parsed_priorities.rule_indices
        self.indice_rules: Dict[int, str] = { index: name for name, index in self.rule_indices.items() }
        self.priorities: dok_matrix = parsed_priorities.priorities
        self.conflict_matrix: dok_matrix = parsed_priorities.conflict_matrix
        self.default: bool = parsed_priorities.default

    # TODO There are priorities which are incosistent, like R1 > R2 > R1. Catch them and throw errors.

    def is_prior(self, rule_1: str, rules: Dict[str, Set[Substitution]], main_sub: Substitution) -> bool: # TODO Consider lists instead of sets?
        # print("rules_values:", [ str(x) for x in rules.values()])
        # print("rules:", [[str(y) for y in x] for x in rules.values()])
        target_head = main_sub.apply(self.rule_heads[rule_1])
        # print(f"\ttarget_head: {target_head}")
        dilemmas: List[FrozenSet[str]] = []
        ind_1: int = self.rule_indices[rule_1]
        is_prior: bool = True
        for rule_2, subs in rules.items():
            # print(f"subs: {type(subs)}")
            if rule_2 == rule_1:
                continue
            actual_conflict = False
            for sub in subs:
                # print(f"sub: {sub}")
                candidate_conflict = sub.apply(self.rule_heads[rule_2])
                # print(f"candidate_conflict: {candidate_conflict}")
                if candidate_conflict.is_conflicting_with(target_head):
                    actual_conflict = True
                    break
            if not actual_conflict:
                continue
            # print("\tActual conflict")
            ind_2: int = self.rule_indices[rule_2]
            if self.conflict_matrix[ind_1, ind_2] and not self.priorities[ind_1, ind_2] and not self.priorities[ind_2, ind_1]:
                dilemmas.append(frozenset([rule_1, rule_2]))
                is_prior = False
                continue
            if not self.priorities[ind_1, ind_2] and self.priorities[ind_2, ind_1]: # TODO Are both checks necessary since you store only 1 for conflicting pairs?
                return False # FIXME Revisit this. Why not `is_prior = False` and then proceed to dilemmas?
        if len(dilemmas) > 0:
            raise UnresolvedConflictsError(dilemmas)
        return is_prior
    
    def __str__(self) -> str:
        if self.default:
            return "default"
        priorities_str: str = ""
        for rule_1, rule_2 in self.priorities.keys():
            priorities_str += self.indice_rules[rule_1] + " > " + self.indice_rules[rule_2] + ";\n"
        return priorities_str.strip()