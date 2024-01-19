from __future__ import annotations
from typing import Dict, Set, List, Tuple, Iterator, overload, Union, FrozenSet
from copy import deepcopy
import re
import numpy as np
from numpy.typing import ArrayLike
from scipy.sparse import dok_matrix
from prudens_core.entities.Literal import Literal
from prudens_core.entities.Rule import Rule
from prudens_core.entities.Context import Context
from prudens_core.entities.Substitution import Substitution
from prudens_core.entities.PriorityRelation import PriorityRelation
from prudens_core.parsers.PolicyParser import ParsedPolicy, PolicyParser
from prudens_core.errors.RuntimeErrors import RuleNotFoundError, LiteralNotInContextError, LiteralAlreadyInContextError, UnresolvedConflictsError
from prudens_core.errors.SyntaxErrors import PrudensSyntaxError, MissingDelimiterError, MultipleDelimiterError
import prudens_core.utilities.utils as utils

class Policy:
    __slots__ = ("original_string", "rules", "rule_hasse_diagram", "priorities", "inferences", "dilemmas", "inferred_by")

    def __init__(self, policy_string: str) -> None:
        self.original_string: str = policy_string
        parser: PolicyParser = PolicyParser(self.original_string)
        try:
            parsed_policy: ParsedPolicy = parser.parse()
        except Exception as e:
            raise e
        self.rules: Dict[str, Rule] = parsed_policy.rules
        self.rule_hasse_diagram: HasseDiagram = HasseDiagram(parsed_policy.rules)
        self.priorities: PriorityRelation = parsed_policy.priorities
        self.inferences: Context = Context()
        self.dilemmas: Dict[Literal, Dilemma] = dict()
        self.inferred_by: Dict[Literal, List[Dict[str, Set[Substitution]]]] = dict()

    @classmethod
    def from_dict(cls, init_dict: Dict) -> Policy:
        policy = cls.__new__(cls)
        policy.original_string = utils.parse_dict_prop(init_dict, "original_string", "Policy", default_value = "", expected_types = [str])
        try:
            rules = init_dict["rules"]
        except KeyError:
            raise KeyError(f"Missing key 'rules' in Policy initialization from dict.")
        if type(rules) != dict:
            raise TypeError(f"Expected input of type 'dict' for Policy.rules but received {type(rules)}.")
        policy.rules = dict()
        for rn, rule in rules.items():
            if type(rn) != str:
                raise TypeError(f"Expected input of type 'str' for Policy.rules.key but received {type(rn)}.")
            try:
                policy.rules[rn] = Rule.from_dict(rule)
            except KeyError as e:
                raise KeyError(f"While parsing a policy from a dict, rule {rn} could not be properly parsed.") from e
            except TypeError as e:
                raise TypeError(f"While parsing a policy from a dict, rule {rn} could not be properly parsed.") from e
            except ValueError as e:
                raise ValueError(f"While parsing a policy from a dict, rule {rn} could not be properly parsed.") from e 
        policy.rule_hasse_diagram = HasseDiagram(policy.rules)
        try:
            priorities = init_dict["priorities"]
        except KeyError:
            raise KeyError(f"Missing key 'priorities' in Policy initialization from dict.")
        if type(priorities) != dict:
            raise TypeError(f"Expected input of type 'dict' for Policy.priorities but received {type(priorities)}.")
        try:
            policy.priorities = PriorityRelation.from_dict(priorities)
        except KeyError as e:
            raise KeyError(f"While parsing a policy from a dict, priorities could not be properly parsed.") from e
        except TypeError as e:
            raise TypeError(f"While parsing a policy from a dict, priorities could not be properly parsed.") from e
        except ValueError as e:
            raise ValueError(f"While parsing a policy from a dict, priorities could not be properly parsed.") from e
        try:
            inferences = init_dict["inferences"]
        except KeyError:
            inferences = dict()
        if type(inferences) != dict:
            raise TypeError(f"Expected input of type 'dict' for Policy.inferences but received {type(inferences)}.")
        try:
            policy.inferences = Context.from_dict(inferences)
        except KeyError as e:
            raise KeyError(f"While parsing a policy from a dict, inferences could not be properly parsed.") from e
        except TypeError as e:
            raise TypeError(f"While parsing a policy from a dict, inferences could not be properly parsed.") from e
        except ValueError as e:
            raise ValueError(f"While parsing a policy from a dict, inferences could not be properly parsed.") from e
        try:
            dilemmas = init_dict["dilemmas"]
        except KeyError:
            dilemmas = dict()
        if type(inferences) != dict:
            raise TypeError(f"Expected input of type 'dict' for Policy.inferences but received {type(dilemmas)}.")
        policy.dilemmas = dict()
        for l, d in dilemmas.items():
            try:
                lit = Literal(l)
            except PrudensSyntaxError as e:
                raise SyntaxError("While parsing a policy from a dict, dilemmas could not be properly parsed.") from e
            try:
                policy.dilemmas[lit] = Dilemma.from_dict()
            except KeyError as e:
                raise KeyError(f"While parsing a policy from a dict, dilemma {d} could not be properly parsed.") from e
            except TypeError as e:
                raise TypeError(f"While parsing a policy from a dict, dilemma {d} could not be properly parsed.") from e
            except ValueError as e:
                raise ValueError(f"While parsing a policy from a dict, dilemma {d} could not be properly parsed.") from e
        try:
            inferred_by = init_dict["inferred_by"]
        except KeyError:
            inferred_by = dict()
        if type(inferences) != dict:
            raise TypeError(f"Expected input of type 'dict' for Policy.inferred_by but received {type(inferred_by)}.")
        policy.inferred_by = dict()
        for l, instances in inferred_by.items():
            try:
                lit = Literal(l)
            except PrudensSyntaxError as e:
                raise SyntaxError("While parsing a policy from a dict, inferred_by could not be properly parsed.") from e
            policy.inferred_by[lit] = []
            for instance_dict in instances:
                if type(instance_dict) != dict:
                    raise TypeError(f"Expected input of type 'dict' for Policy.inferred_by.literal.values but received {type(instance_dict)}.")
                for rn, sub_list in instance_dict.items():
                    if type(rn) != str:
                        raise TypeError(f"Expected input of type 'str' for rule name but received {type(rn)}.")
                    if type(sub_list) != list:
                        raise TypeError(f"Expected input of type 'list' for list of subs but received {type(sub_list)}.")
                    for s in sub_list:
                        try:
                            sub = Substitution.from_dict(s)
                        except KeyError as e:
                            raise KeyError(f"While parsing a policy from a dict, substitution {s} could not be properly parsed.") from e
                        except TypeError as e:
                            raise TypeError(f"While parsing a policy from a dict, substitution {s} could not be properly parsed.") from e
                        except ValueError as e:
                            raise ValueError(f"While parsing a policy from a dict, substitution {s} could not be properly parsed.") from e
                        policy.inferred_by[lit].append(sub)
        return policy

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "rules": { rn: rule.to_dict() for rn, rule in self.rules.items() },
            "priorities": self.priorities.to_dict(),
            "inferences": self.inferences.to_dict(),
            "dilemmas": { str(l): d.to_dict() for l, d in self.dilemmas.items() }, # TODO Implement `to_dict()` for dilemmas!
            "inferred_by": { str(l): [
                { rn: sub.to_dict() for rn, sub in instance_dict.items() } for instance_dict in inferring_rules
            ] for l, inferring_rules in self.inferred_by.items() }, # TODO Implement `to_dict()` for substitutions!
        }

    def infer(self,
              context: Context,
              max_depth: float = np.inf,
              unittest_params: Union[None, Dict] = None) -> None:
        inference_graph: InferenceGraph = InferenceGraph(self.rules,
                                                         self.rule_hasse_diagram,
                                                         context,
                                                         unittest_params = unittest_params)
        # print("=" * 25)
        # print("ig complete")
        marked_literals: Context = context
        dilemmas: Dict[Literal, Dilemma] = dict()
        inferred: bool = True
        depth: int = 0
        while inferred and depth < max_depth:
            inferred = False
            inference_graph.remove_conflicts_with(marked_literals)
            inferring_rules: Dict[str, Set[Substitution]] = inference_graph.get_consistent_rules()
            # print("inf rules keys:", inferring_rules.keys())
            # print("inf rules values:", [[str(x) for x in v] for v in inferring_rules.values()])
            for rule_name in self.rule_hasse_diagram:
                # print("rule:", rule_name)
                if rule_name not in inferring_rules.keys():
                    continue
                # print("rule in inferring rules")
                # print(f"inferring_rules[{rule_name}]:", {str(x) for x in inferring_rules[rule_name]})
                rule: Rule = self.rules[rule_name]
                for sub in inferring_rules[rule_name]:
                    # self.rule_hasse_diagram.update_last_call(False)
                    if not rule.is_triggered(marked_literals, sub):
                        self.rule_hasse_diagram.update_last_call(False)
                        continue
                    instance: Literal = sub.apply(rule.head)
                    try:
                        is_prior: bool = self.priorities.is_prior(rule_name, inferring_rules, sub)
                    except UnresolvedConflictsError as e:
                        is_prior: bool = False
                        new_dilemma: Dilemma = Dilemma(sub.apply(rule.head), set(e.conflicts))
                        positive_head: Literal = new_dilemma.literal
                        # new_dilemmas: List[FrozenSet[str, str]] = e.conflicts
                        # print("Before:", positive_head, [str(x) for x in dilemmas.keys()])
                        if positive_head in dilemmas.keys():
                            dilemmas[positive_head] = dilemmas[positive_head].union(new_dilemma)
                        else:
                            dilemmas[positive_head] = new_dilemma
                    # print("After:", positive_head, [str(x) for x in dilemmas.keys()])
                    # print("\tis_prior:", is_prior)
                    if not is_prior:
                        # self.rule_hasse_diagram.update_last_call(False) # FIXME Should this also be updated based on subs?
                        continue
                    # print("rule is prior")
                    # print("Literal not in context error")
                    # self.rule_hasse_diagram.update_last_call(True)
                    # instance: Literal = sub.apply(rule.head)
                    # print("instance:", instance, "sub:", sub)
                    try:
                        marked_literals.add_literal(instance)
                    except LiteralAlreadyInContextError:
                        continue
                    inferred = True
                    if not instance in self.inferred_by.keys(): # FIXME Again, this has been computed. Nevertheless, is it efficient to remove elements from ig.inferred_by or is this more/equally efficient?
                        self.inferred_by[instance] = { rule_name: set([sub]) }
                    elif not rule_name in self.inferred_by[instance].keys():
                        self.inferred_by[instance][rule_name] = set([sub])
                    else:
                        self.inferred_by[instance][rule_name].add(sub)
            depth += 1
        # print("depth:", depth)
        # print("Marked literals: ", marked_literals)
        self.inferences = marked_literals
        self.dilemmas = dilemmas
    
    def __str__(self) -> str:
        policy_str: str = "@Policy\n"
        for rule in self.rules.values():
            policy_str += str(rule) + ";\n"
        policy_str += "\n@Priorities\n" + str(self.priorities)
        return policy_str

class Dilemma:
    """This class is used merely for unit testing facilitation, so it is not intended for broader use."""

    __slots__ = ("literal", "conflicts")

    def __init__(self, literal: Literal = None, conflicts: Set[FrozenSet[str]] = None) -> None:
        """`self.literal` is always a positive instance of the literal!"""
        if literal and conflicts:
            positive_literal: Literal = deepcopy(literal)
            positive_literal.sign = True
            self.literal: Literal = positive_literal
            self.conflicts: Set[FrozenSet[str]] = conflicts

    @classmethod
    def from_string(cls, dilemma_str: str) -> Dilemma:
        """General dilemma syntax: literal_str: [{rule_11, rule_12}, {rule_21, rule_22},..., {rule_n1, rule_n2}]."""
        dilemma = cls.__new__(cls)
        split_dilemma = dilemma_str.split(":")
        if len(split_dilemma) == 1:
            raise MissingDelimiterError(":")
        if len(split_dilemma) > 2:
            raise MultipleDelimiterError(":")
        try:
            dilemma.literal = Literal(split_dilemma[0].strip())
        except PrudensSyntaxError as e:
            raise e
        conflict_delim = r'(?<=\})\s*,'
        # FIXME You need to throw proper exceptions at this point!
        conflicts_set = set()
        # # print("conflicts after split_delim:", conflicts)
        for conflict in re.split(conflict_delim, split_dilemma[1].strip()[1:-1]):
            conflict = conflict.strip()
            if not conflict:
                continue
            conflict = conflict[1:-1]
            # # print("trimmed conflict:", conflict)
            rules = conflict.split(",")
            conflicts_set.add(frozenset([x.strip() for x in rules]))
        # # print(conflicts_set)
        dilemma.conflicts = conflicts_set
        return dilemma

    @classmethod
    def from_dict(cls, init_dict: Dict) -> Dilemma:
        dilemma = cls.__new__(cls)
        try:
            literal = init_dict["literal"]
        except KeyError:
            raise KeyError(f"Missing key 'literal' in Dilemma initialization from dict.")
        try:
            dilemma.literal = Literal.from_dict(literal)
        except KeyError as e:
            raise KeyError(f"While parsing a dilemma from a dict, literal {literal} could not be properly parsed.") from e
        except TypeError as e:
            raise TypeError(f"While parsing a dilemma from a dict, literal {literal} could not be properly parsed.") from e
        except ValueError as e:
            raise ValueError(f"While parsing a dilemma from a dict, literal {literal} could not be properly parsed.") from e
        try:
            conflicts = init_dict["conflicts"]
        except KeyError:
            raise KeyError(f"Missing key 'conflicts' in Dilemma initialization from dict.")
        dilemma.conflicts = set()
        for cs in conflicts:
            if type(cs) != list:
                raise TypeError(f"Expected input of type 'list' for Dilemma.conflicts.value but received {type(cs)}.")
            for c in cs:
                if type(c) != str:
                    raise TypeError(f"Expected input of type 'str' for dilemma conflict (rule name) but received {type(c)}.")
                dilemma.conflicts.add(frozenset(c))
        return dilemma

    def to_dict(self) -> Dict:
        return {
            "literal": self.literal.to_dict(),
            "conflicts": [ list(x) for x in self.conflicts ],
        }

    def append_conflict(self, conflict: FrozenSet[str]) -> None:
        self.conflicts.add(conflict)

    def union(self, other: Dilemma) -> Dilemma:
        union_dilemma: Dilemma = self.__deepcopy__()
        union_dilemma.conflicts = union_dilemma.conflicts.union(other.conflicts)
        # for conflict in other.conflicts:
        #     union_dilemma.append_conflict(conflict)
        return union_dilemma
    
    def __deepcopy__(self, memodict = {}) -> Dilemma:
        copycat: Dilemma = Dilemma()
        copycat.literal = deepcopy(self.literal)
        copycat.conflicts = {x for x in self.conflicts}
        return copycat

    def __eq__(self, __other: object) -> bool:
        # # print(str(self), str(__other))
        if not isinstance(__other, Dilemma):
            return False
        if self.literal != __other.literal:
            return False
        for conflict in self.conflicts:
            if conflict not in __other.conflicts:
                return False
        return True
    
    def __str__(self) -> str:
        return str(self.literal) + ": [" + ", ".join(["{" + ", ".join(x) + "}" for x in self.conflicts]) + "]"

class InferenceGraph:
    __slots__ = ("rules", "rule_hd", "context", "inferred_by", "inferences", "consistent")

    def __init__(self,
                 rules: Dict[str, Rule],
                 rule_hd: HasseDiagram,
                 context: Context,
                 unittest_params: Union[None, Dict] = None) -> None:
        self.rules: Dict[str, Rule] = rules
        self.rule_hd: HasseDiagram = rule_hd # FIXME Maybe deepcopy this.
        self.context: Context = context
        self.inferred_by: Dict[Literal, List[Dict[str, Set[Substitution]]]] = dict()
        self.inferences: Context = Context()
        self.consistent: Context = Context()
        # print("init complete\n" + "=" * 40)
        self.__compute_ig(unittest_params = unittest_params)
        # print(str(self.inferences))
        # Just to stringify
        # str_inf_by = { str(key): { x: [str(s) for s in y] for x, y in val.items() } for key, val in self.inferred_by.items() }
        # print("str_inf_by:", str_inf_by)
    
    def __compute_ig(self, max_depth: float = np.inf, unittest_params: Union[None, Dict] = None) -> None:
        inferred: bool = True
        facts: Context = deepcopy(self.context)
        depth: int = 0
        hd_iterations: int = 0
        inferred_by: Dict[Literal, List[Dict[str, List[Substitution]]]] = dict()
        while inferred and depth < max_depth:
            inferred = False
            for rule_name in self.rule_hd:
                # print("In the loop:", rule_name)
                hd_iterations += 1
                # print("~" * 50 +  "\nrule:", rule_name)
                rule: Rule = self.rules[rule_name]
                try:
                    # print("facts:", facts)
                    inferences = rule.trigger(facts)
                    # print("rule inferences:", [[str(y) for y in x] for x in inferences])
                except LiteralNotInContextError:
                    # print("in ig rule name:", rule_name)
                    self.rule_hd.update_last_call(False)
                    continue
                self.rule_hd.update_last_call(True)
                for literal, sub in inferences:
                    try:
                        facts.add_literal(literal)
                    except LiteralAlreadyInContextError:
                        if literal in self.context:
                            continue
                        if not rule_name in inferred_by[literal].keys():
                            inferred_by[literal][rule_name] = set([sub])
                        else:
                            inferred_by[literal][rule_name].add(sub)
                        continue
                    inferred = True
                    if not literal in inferred_by.keys():
                        inferred_by[literal] = { rule_name: set([sub]) }
                    elif not rule_name in inferred_by[literal].keys():
                        inferred_by[literal][rule_name] = set([sub])
                    else:
                        inferred_by[literal][rule_name].add(sub)
            depth += 1
        self.inferences = facts
        # print("inferred_by:", {str(l): {str(k): {str(x) for x in val} for k, val in v.items()} for l, v in inferred_by.items()})
        self.inferred_by = inferred_by
        self.consistent = deepcopy(self.inferences) # FIXME This ensures an absurd behaviour if called before remove_conflicts_with
        if unittest_params:
            unittest_params["depth"] = depth
            unittest_params["hd_iterations"] = hd_iterations

    def remove_conflicts_with(self, marked: List[Literal]) -> Context:
        # print("marked:", marked)
        self.consistent.remove_conflicts_with(marked)

    def get_consistent_rules(self) -> Dict[str, Set[Substitution]]:
        # instances: Set[str] = set()
        instances: Dict[str, Set[Substitution]] = dict()
        # print("inferred by:", self.inferred_by.keys())
        # print("self.consistent:", self.consistent)
        # print("self.inferred_by.keys():", [str(x) for x in self.inferred_by.keys()])
        for literal in self.consistent:
            # print("literal:", literal)
            if literal not in self.inferred_by.keys():
                # print("NOT EQUAL!")
                continue
            # print("EQUAL")
            for rule_name, subs in self.inferred_by[literal].items():
                if rule_name not in instances.keys():
                    instances[rule_name] = subs
                else:
                    instances[rule_name] = instances[rule_name].union(subs)
            # instances = instances.union(set(self.inferred_by[literal].keys()))
        return instances
    
    """Add and remove rules in an inference graph in a consistent way that saves up time. The same might apply
    to contexts, as well."""

class HasseDiagram: # Implemented specifically for use within Prudens, not for wider audience.
    __slots__ = ("_last_call", "nodes", "layers", "node_indices", "node_indices_rev", "front",
                 "existing_layers", "edges")

    def __init__(self, nodes: Dict[str, Rule]) -> None:
        self._last_call: LastCall = LastCall("")
        self.__initialize_nodes(nodes)
        self.__initialize_edges()
        # print("self.nodes:", {str(item[0]): str(item[1]) for item in self.nodes.items()})

    def __initialize_nodes(self, nodes: Dict[str, Rule]) -> None:
        self.nodes: Dict[RuleSignature: List[str]] = dict()
        self.layers: Dict[int, List[RuleSignature]] = dict()
        self.node_indices: Dict[RuleSignature: int] = dict()
        self.node_indices_rev: Dict[int, RuleSignature] = dict()
        for name, rule in nodes.items():
            signature: RuleSignature = RuleSignature(rule.signature)
            signature_size: int = len(signature)
            if signature not in self.nodes.keys():
                self.nodes[signature] = [name]
            else:
                self.nodes[signature].append(name)
            if signature_size not in self.layers.keys():
                self.layers[signature_size] = [signature]
            elif signature not in self.layers[signature_size]:
                self.layers[signature_size].append(signature)
        node_keys = list(self.nodes.keys())
        self.front: List[RuleSignature] = node_keys[:]
        self.node_indices = { node_keys[i]: i for i in range(len(node_keys)) }
        self.node_indices_rev = { item[1]: item[0] for item in self.node_indices.items() }
        self.existing_layers: List[int] = sorted(list(self.layers.keys()))

    def __initialize_edges(self) -> None:
        n: int = len(self.nodes)
        edges: ArrayLike = np.zeros((n, n)) # TODO Revisit this! Maybe a set of tuples? Check what operations you make on edges!
        self.edges: dok_matrix = dok_matrix(edges)
        for signature in self.nodes.keys():
            self.__update_edges(signature)

    def __update_edges(self, signature: RuleSignature) -> None:
        signature_size: int = len(signature)
        layer_index: int = self.existing_layers.index(signature_size)
        node_index: int = self.node_indices[signature]
        super_added: List[int] = []
        super_excluded: List[RuleSignature] = []
        for super_layer in self.existing_layers[(layer_index + 1):]:
            for super_signature in self.__exclude_supersets(super_excluded, self.layers[super_layer][:]):
                if signature.is_subsignature(super_signature):
                    super_index: int = self.node_indices[super_signature]
                    self.edges[node_index, super_index] = 1
                    super_added.append(super_index)
                super_excluded.append(super_signature)
        sub_added: List[int] = []
        sub_excluded: List[RuleSignature] = []
        for sub_layer in self.existing_layers[:layer_index]:
            for sub_signature in self.__exclude_subsets(sub_excluded, self.layers[sub_layer][:]):
                if sub_signature.is_subsignature(signature):
                    sub_index: int = self.node_indices[sub_signature]
                    self.edges[sub_index, node_index] = 1
                    sub_added.append(sub_index)
                sub_excluded.append(sub_signature)
        for end_node in super_added:
            for start_node in sub_added:
                self.edges[start_node, end_node] = 0

    def __exclude_supersets(self, sub_signatures: List[RuleSignature], signatures: List[RuleSignature]) -> List[RuleSignature]:
        if len(sub_signatures) == 0:
            for x in signatures:
                yield x
        for signature in signatures:
            i = 0
            while i < len(sub_signatures) and not sub_signatures[i].is_subsignature(signature):
                i += 1
            if i == len(sub_signatures):
                yield signature
    
    def __exclude_subsets(self, super_signatures: List[RuleSignature], signatures: List[RuleSignature]) -> List[RuleSignature]:
        if (len(super_signatures)) == 0:
            for x in signatures:
                yield x
        for signature in signatures:
            i = 0
            while i < len(super_signatures) and not signature.is_subsignature(super_signatures[i]):
                i += 1
            if i == len(super_signatures):
                yield signature
    
    def add_node(self, common_signature: str, rules: List[str]) -> None:
        signature: RuleSignature = RuleSignature(common_signature)
        signature_size: int = len(signature)
        if signature not in self.nodes.keys():
            n: int = len(self.nodes)
            self.node_indices[signature] = n
            self.node_indices_rev[n] = signature
            self.edges.resize((n + 1, n + 1))
            self.edges.reshape((n + 1, n + 1))
            self.nodes[signature] = rules
        else:
            for rule in rules:
                self.nodes[signature].append(rule) # TODO Check for actual duplicates?
        if signature_size not in self.existing_layers:
            self.layers[signature_size] = [signature]
            self.__add_layer(signature_size)
        else:
            self.layers[signature_size].append(signature)
        self.__update_edges(signature)

    def __add_layer(self, layer: int) -> None:
        n: int = len(self.existing_layers)
        length: int = n // 2
        pivot: int = n // 2
        while length > 0:
            length //= 2
            if layer < self.existing_layers[pivot]:
                pivot -= length
            else:
                pivot += length
        self.existing_layers.insert(pivot + 1, layer)

    def remove_rule(self, rule: Rule) -> None:
        signature: RuleSignature = RuleSignature(rule.signature)
        try:
            self.nodes[signature].remove(rule.name) # TODO Does this work with objects?
        except ValueError:
            raise RuleNotFoundError
        if len(self.nodes[signature]) == 0:
            self.__remove_node(signature)

    def __remove_node(self, signature) -> None:
        n: int = len(self.nodes)
        signature_size: int = len(signature)
        node_index: int = self.node_indices[signature]
        del self.nodes[signature]
        del self.node_indices[signature]
        del self.node_indices_rev[node_index]
        for node, index in self.node_indices.items():
            if index > node_index:
                self.node_indices[node] = index - 1
                self.node_indices_rev[index - 1] = node
        old_ends: List[int] = []
        old_starts: List[int] = []
        for i in range(n):
            if self.edges[node_index, i] == 1:
                old_ends.append(i)
                del self.edges[node_index, i]
            if self.edges[i, node_index] == 1:
                old_starts.append(i)
                del self.edges[i, node_index]
        for start in old_starts:
            for end in old_ends:
                self.edges[start, end] = 1
        self.edges.resize((n - 1, n - 1))
        self.edges.reshape((n - 1, n - 1))
        self.layers[signature_size].remove(signature)
        if len(self.layers[signature]) == 0:
            self.__remove_layer(signature_size)

    def __remove_layer(self, layer: int) -> None:
        del self.layers[layer]
        self.existing_layers.remove(layer)

    def __next__(self) -> str:
        if not self._last_call:
            # print("not self._last_call")
            layer: List[RuleSignature] = self.layers[self.existing_layers[0]]
            signature: RuleSignature = layer[0]
            name: str = self.nodes[signature][0]
            # print(self.front)
            self._last_call.signature = signature
            self._last_call.index = 0
            # self._last_call.min_layer_index = 0
            # self._last_call.layer_index = 0
            self.front = [x for x in self.nodes.keys() if x != signature or len(self.nodes[signature]) != 1] # FIXME How to handle rules with same signature?
            self.front.sort(key = lambda x: len(x))
            # self.front = list(self.nodes.keys()) # FIXME This is a bit profligate...
            # print("front:", [str(x) for x in self.front])
            # print("self._last_call:", self._last_call.signature)
            return name
        if not self._last_call.triggered:
            # print("Before prunning:", self.front)
            self.__prune_front()
            # print("After prunning:", self.front)
        if len(self.front) == 0 and self._last_call.index == len(self.nodes[self._last_call.signature]) - 1:
            # print("empty front")
            # print("self._last_call.index:", self._last_call.index)
            # print("self.nodes[self._last_call.signature]:", self.nodes[self._last_call.signature])
            self._last_call = LastCall("")
            self.front = list(self.nodes.keys())[:]
            raise StopIteration
        if self._last_call.index < len(self.nodes[self._last_call.signature]) - 1:
            next_rule = self.nodes[self._last_call.signature][self._last_call.index + 1]
            # print("last if")
            # print("next_rule:", next_rule)
            # print("self._last_call.signature:", self._last_call.signature)
            self._last_call.index += 1
            return next_rule
        # # print([str(x) for x in self.front])
        # # print(str(self._last_call.signature))
        # FIXME What was the purpose of the following exception handling?
        # try: # TODO Check this part again? Should there be cases where the signature has already been removed?
        #     # # print(self.front[0])
        #     self.front.remove(self._last_call.signature)
        #     # # print("Signature removed!")
        # except ValueError:
        #     pass
        # print("self._last_call.index:", self._last_call.index)
        # print("self.nodes[self._last_call.signature]:", self.nodes[self._last_call.signature])
        # if self._last_call.layer_index == len(self.layers[self.existing_layers[self._last_call.min_layer_index]]):
        #     self._last_call.min_layer_index += 1
        #     self.layer_index = 0
        # print("min_layer:", self._last_call.min_layer_index)
        # print("existing layers:", self.existing_layers)
        signature: RuleSignature = self.front.pop(0) # TODO Consider adding a "LastCall.reset()" method to tidy this up!
        self._last_call.signature = signature
        self._last_call.index = 0
        # print("Popping another one:", signature)
        # self.last_rule = { "signature": signature, "index": 0 }
        return self.nodes[signature][0]

    def __prune_front(self) -> None:
        last_signature: RuleSignature = self._last_call.signature
        # print("last_signature:", last_signature)
        n: int = len(self.front)
        i: int = 0
        # print(i, n)
        while i < n:
            # print(f"i: {i}, n: {n}")
            front_signature: RuleSignature = self.front[i]
            # print("front_signature:", front_signature)
            if last_signature.is_subsignature(front_signature):
                # print(last_signature, "is subsignature of", front_signature)
                before, total = self.__prune_branch(self.node_indices[front_signature]) # FIXME Annotation? Tuple[int, int]
                i -= before
                n -= total
            else:
                # print("else")
                i += 1
                
    def __prune_branch(self, index: int) -> Tuple[int]: # FIXME You might calculate the branch wrongly, in __get_children_indices()!
        # print("index:", index)
        # print("self.front:", [str(x) for x in self.front])
        branch_front: List[int] = [index]
        before: int = 0
        total: int = 0
        while len(branch_front) > 0:
            current: RuleSignature = branch_front.pop()
            children: List[int] = self.__get_children_indices(current)
            # print(f"\tcurrent: {self.node_indices_rev[current]}\n\tchildren: {[str(self.node_indices_rev[i]) for i in children]}")
            branch_front += children
            try:
                # print(f"Trying to remove: {self.node_indices_rev[current]}")
                self.front.remove(self.node_indices_rev[current])
                # print(f"Success!\n{'=' * 50}")
            except ValueError:
                # print(f"Failure!\n{'=' * 50}")
                pass
            if current < index:
                before += 1
            total += 1
        return (before, total)

    def __get_children_indices(self, index: int) -> List[int]:
        n: int = len(self.nodes)
        children: List[int] = []
        for i in range(n):
            if self.edges[index, i] == 1:
                children.append(i)
        return children

    def update_last_call(self, triggered: bool):
        self._last_call.triggered = triggered

    def __iter__(self) -> HasseDiagram:
        return self

class RuleSignature: # TODO Consider moving this to rule and fix all instances of rule.signature accordingly.
    __slots__ = ("signature", "literal_signatures", "length")
    
    def __init__(self, signature: str) -> None:
        self.signature: str = signature
        self.literal_signatures: List[str] = self.signature.split("|")
        self.length: int = len(self.literal_signatures)

    def is_subsignature(self, other: RuleSignature) -> bool:
        start_index: int = 0
        # print(f"is_subsignature({self}, {other})")
        # print(f"literal_signatures: {self.literal_signatures}")
        for literal in self.literal_signatures:
            # print(f"\tliteral: {literal}")
            try:
                found_index: int = other.literal_signatures[start_index:].index(literal)
                # print(f"\tfound_index: {found_index}")
            except ValueError:
                # print("False")
                return False
            start_index = found_index
            # print(f"\tstart_index: {start_index}")
        # print("True")
        return True

    @overload
    def __getitem__(self, key: int) -> str:
        ...
    
    @overload
    def __getitem__(self, key: slice) -> List[str]:
        ...
    
    def __getitem__(self, key: Union[int, slice]) -> Union[str, List[str]]:
        if isinstance(key, slice):
            return self.literal_signatures[key]
        return self.literal_signatures[key.__index__()]

    def __iter__(self) -> Iterator:
        return self.literal_signatures

    def __len__(self) -> int:
        return self.length
    
    def __eq__(self, other: RuleSignature) -> bool:
        # # print("in __eq__")
        # # print(self, other)
        if not isinstance(other, RuleSignature):
            return False
        return self.signature == other.signature

    def __hash__(self) -> int:
        return hash(self.signature)
    
    def __str__(self) -> str:
        return self.signature
    
class LastCall:
    __slots__ = ("signature", "index", "triggered")

    def __init__(self, signature: RuleSignature, index: int = -1) -> None:
        if signature == "":
            self.signature: RuleSignature = RuleSignature("")
        else:
            self.signature: RuleSignature = signature
        self.index: int = index
        # self.min_layer_index: int = min_layer_index
        self.triggered: bool = True
        # self.layer_index: int = layer_index

    def __bool__(self) -> bool:
        return len(self.signature) != 0 and self.index > -1# and self.min_layer_index > -1 and self.layer_index > -1