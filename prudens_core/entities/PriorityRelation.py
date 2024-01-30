from __future__ import annotations
from typing import Dict, Set, List, FrozenSet, Tuple
from prudens_core.entities.Literal import Literal
from prudens_core.entities.Rule import Rule
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.PriorityRelationParser import (
    PriorityRelationParser,
    ParsedPriorityRelation,
)
from prudens_core.errors.RuntimeErrors import UnresolvedConflictsError
import prudens_core.utilities.utils as utils


class PriorityRelation:
    __slots__ = (
        "original_string",
        "rule_heads",
        "rule_indices",
        "indice_rules",
        "priorities",
        "conflict_matrix",
        "default",
        "candidate_conflicts",
    )

    def __init__(self, priority_str: str, rules: Dict[str, Rule]) -> None:
        self.original_string: str = priority_str
        parser: PriorityRelationParser = PriorityRelationParser(
            self.original_string, rules
        )
        try:
            parsed_priorities: ParsedPriorityRelation = parser.parse()
        except Exception as e:
            raise e
        self.rule_heads: Dict[str, Literal] = {
            rule_name: rule.head for rule_name, rule in rules.items()
        }
        self.candidate_conflicts: Dict[str, Set[str]] = {
            rn_1: {
                rn_2
                for rn_2, r_2 in rules.items()
                if r_1.head.name == r_2.head.name and r_1.head.sign != r_2.head.sign
            }
            for rn_1, r_1 in rules.items()
        }
        self.rule_indices: Dict[str, int] = parsed_priorities.rule_indices
        self.indice_rules: Dict[int, str] = {
            index: name for name, index in self.rule_indices.items()
        }
        self.priorities: Set[Tuple[int]] = parsed_priorities.priorities
        self.default: bool = parsed_priorities.default

    # TODO There are priorities which are incosistent, like R1 > R2 > R1. Catch them and throw errors.

    @classmethod
    def from_dict(cls, init_dict) -> PriorityRelation:
        pr = cls.__new__(cls)
        pr.original_string = utils.parse_dict_prop(
            init_dict,
            "original_string",
            "PriorityRelation",
            default_value="",
            expected_types=[str],
        )
        pr.default = utils.parse_dict_prop(
            init_dict, "default", "PriorityRelation", expected_types=[bool]
        )
        try:
            rule_heads = init_dict["rule_heads"]
        except KeyError:
            raise KeyError(
                f"Missing key 'rule_heads' in PriorityRelation initialization from dict."
            )
        if type(rule_heads) != dict:
            raise TypeError(
                f"Expected input of type 'dict' for PriorityRelation.rule_heads but received {type(rule_heads)}."
            )
        pr.rule_heads = dict()
        for rn, head in rule_heads.items():
            if type(rn) != str:
                raise TypeError(
                    f"Expected input of type 'str' for PriorityRelation.rule_heads.key but received {type(rn)}."
                )
            try:
                pr.rule_heads[rn] = Literal.from_dict(head)
            except KeyError as e:
                raise KeyError(
                    f"While parsing priority relation from a dict, literal dict {head} in provided rule_heads "
                    "could not be properly parsed to a literal."
                ) from e
            except TypeError as e:
                raise TypeError(
                    f"While parsing priority relation from a dict, literal dict {head} in provided rule_heads "
                    "could not be properly parsed to a literal."
                ) from e
            except ValueError as e:
                raise ValueError(
                    f"While parsing priority relation from a dict, literal dict {head} in provided rule_heads "
                    "could not be properly parsed to a literal."
                ) from e
        pr.candidate_conflicts = {
            rn_1: {
                rn_2
                for rn_2, rh_2 in pr.rule_heads.items()
                if rh_1.name == rh_2.name and rh_1.sign != rh_2.sign
            }
            for rn_1, rh_1 in pr.rule_heads.items()
        }
        # try:
        #     candidate_conflicts = init_dict["candidate_conflicts"]
        # except KeyError:
        #     raise KeyError(f"Missing key 'candidate_conflicts' in PriorityRelation initialization from dict.")
        # if type(candidate_conflicts) != dict:
        #     raise TypeError(f"Expected input of type 'dict' for PriorityRelation.candidate_conflicts but received {type(candidate_conflicts)}.")
        # pr.candidate_conflicts = dict()
        # for rn, ccs in candidate_conflicts.items():
        #     if type(rn) != str:
        #         raise TypeError(f"Expected input of type 'str' for PriorityRelation.candidate_conflicts.keys but received {type(rn)}.")
        #     cc_set = set()
        #     for cc in ccs:
        #         if type(cc) != str:
        #             raise TypeError(f"Expected input of type 'str' for PriorityRelation.candidate_conflicts.values but received {type(cc)}.")
        #         cc_set.add(cc)
        #     pr.candidate_conflicts[rn] = cc_set
        try:
            rule_indices = init_dict["rule_indices"]
        except KeyError:
            raise KeyError(
                f"Missing key 'rule_indices' in PriorityRelation initialization from dict."
            )
        if type(rule_indices) != dict:
            raise TypeError(
                f"Expected input of type 'dict' for PriorityRelation.rule_indices but received {type(rule_indices)}."
            )
        pr.rule_indices = dict()
        for k, v in rule_indices.items():
            if type(k) != str:
                raise TypeError(
                    f"Expected input of type 'str' for PriorityRelation.rule_indices.keys but received {type(k)}."
                )
            if type(v) != int:
                raise TypeError(
                    f"Expected input of type 'int' for PriorityRelation.rule_indices.values but received {type(v)}."
                )
            pr.rule_indices[k] = v
        pr.indice_rules = {v: k for k, v in pr.rule_indices.items()}
        try:
            priorities = init_dict["priorities"]
        except KeyError:
            raise KeyError(
                f"Missing key 'priorities' in PriorityRelation initialization from dict."
            )
        if type(priorities) != list:
            raise TypeError(
                f"Expected input of type 'list' for PriorityRelation.priorities but received {type(priorities)}."
            )
        pr.priorities = set()
        for p in priorities:
            if len(p) != 2:
                raise ValueError(f"Priority contains {len(p)} values. Expected 2.")
            if type(p) != list:
                raise TypeError(
                    f"Expected input of type 'list' for PriorityRelation.priorities.priority but received {type(p)}."
                )
            if type(p[0]) != int:
                raise TypeError(
                    f"Expected input of type 'int' in priority {p} as a first element but received {type(p[0])}."
                )
            if type(p[1]) != int:
                raise TypeError(
                    f"Expected input of type 'int' in priority {p} as a second element but received {type(p[1])}."
                )
            pr.priorities.add(tuple(p))
        return pr

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "rule_heads": {rn: head.to_dict() for rn, head in self.rule_heads.items()},
            "rule_indices": self.rule_indices,
            "priorities": [list(p) for p in self.priorities],
            "default": self.default,
        }

    def is_prior(
        self, rule_1: str, rules: Dict[str, Set[Substitution]], main_sub: Substitution
    ) -> bool:
        # print("rules_values:", [ str(x) for x in rules.values()])
        # print("rules:", [[str(y) for y in x] for x in rules.values()])
        target_head = main_sub.apply(self.rule_heads[rule_1])
        # print(f"\ttarget_head: {target_head}")
        dilemmas: List[FrozenSet[str]] = []
        ind_1: int = self.rule_indices[rule_1]
        is_prior: bool = True
        for rule_2 in self.candidate_conflicts[rule_1].intersection(
            rules.keys()
        ):  # This is better than using `filter()`.
            actual_conflict = False
            for sub in rules[rule_2]:
                # print(f"sub: {sub}")
                # candidate_conflict = sub.apply(self.rule_heads[rule_2])
                # print(f"candidate_conflict: {candidate_conflict}")
                if target_head.is_conflicting_with(sub.apply(self.rule_heads[rule_2])):
                    actual_conflict = True
                    break
            if not actual_conflict:
                continue
            # print("\tActual conflict")
            ind_2: int = self.rule_indices[rule_2]
            # if self.conflict_matrix[ind_1, ind_2] and not self.priorities[ind_1, ind_2] and not self.priorities[ind_2, ind_1]:
            if (ind_1, ind_2) not in self.priorities and (
                ind_2,
                ind_1,
            ) not in self.priorities:
                dilemmas.append(frozenset([rule_1, rule_2]))
                is_prior = False
                continue
            if (ind_1, ind_2) not in self.priorities:
                return False
                # You need not use `is_prior = False` and then proceed to dilemmas because any dilemmas will be captured by rule_2.
        if len(dilemmas) > 0:
            raise UnresolvedConflictsError(dilemmas)
        return is_prior

    def __str__(self) -> str:
        if self.default:
            return "default"
        priorities_str: str = ""
        for rule_1, rule_2 in self.priorities:
            priorities_str += (
                self.indice_rules[rule_1] + " > " + self.indice_rules[rule_2] + ";\n"
            )
        return priorities_str.strip()
