from __future__ import annotations
from typing import Union, Dict, List
from copy import deepcopy
from prudens_core.entities.Literal import Literal
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.ContextParser import ContextParser
from prudens_core.errors.RuntimeErrors import LiteralNotInContextError, LiteralAlreadyInContextError
import prudens_core.utilities.utils as utils

class Context:
    __slots__ = ("original_string", "facts", "_current_bucket", "_current_bucket_index",
                 "_buckets", "_length")

    def __init__(self, context_str: str = "") -> None:
        self.original_string: str = context_str
        self.facts: Dict[int, List[Literal]] = dict()
        self._current_bucket: int = -1
        self._current_bucket_index: int = -1
        self._buckets: List[int] = []
        self._length: int = 0
        if context_str:
            parser: ContextParser = ContextParser(self.original_string)
            try:
                facts: List[Literal] = parser.parse()
            except Exception as e:
                raise e
            for fact in facts:
                self.add_literal(fact)
        """Some notes here:
        self.facts is not just a dict, but actually a bucket hash-table, i.e., a dict with partial hashes as keys
        and lists of literals as values, such that each literal in the list has the same partial hash value."""

    @classmethod
    def from_dict(cls, init_dict: Dict) -> Context:
        context = cls.__new__(cls)
        context.original_string = utils.parse_dict_prop(init_dict, "original_string", "Context", default_value = "", expected_types = [str])
        context._current_bucket = utils.parse_dict_prop(init_dict, "current_bucket", "Context", default_value = -1, expected_types = [int])
        context._current_bucket_index = utils.parse_dict_prop(init_dict, "current_bucket_index", "Context", default_value = -1, expected_types = [int])
        context._buckets = utils.parse_dict_prop(init_dict, "buckets", "Context", default_value = [], expected_types = [list])
        context._length = utils.parse_dict_prop(init_dict, "length", "Context", default_value = 0, expected_types = [int])
        try:
            context_facts = init_dict["facts"]
        except KeyError:
            raise KeyError(f"Missing key 'facts' in Context initialization from dict.")
        if type(context_facts) != dict:
            raise TypeError(f"Expected input of type 'dict' for Context.facts but received {type(context_facts)}.")
        context.facts = dict()
        for bucket, literals in context_facts.items():
            context.facts[bucket] = []
            for l in literals:
                try:
                    context_facts[bucket].append(l.from_dict())
                except KeyError as e:
                    raise KeyError(f"While parsing context from a dict, literal dict {l} could not be properly "
                                   "parsed to a literal.") from e
                except TypeError as e:
                    raise TypeError(f"While parsing context from a dict, literal dict {l} could not be properly "
                                   "parsed to a literal.") from e
                except ValueError as e:
                    raise ValueError(f"While parsing context from a dict, literal dict {l} could not be properly "
                                   "parsed to a literal.") from e
        return context

    def to_dict(self) -> Dict:
        return {
            "original_string": self.original_string,
            "facts": { k: [l.to_dict() for l in v] for k, v in self.facts.items() },
            "current_bucket": self._current_bucket,
            "current_bucket_index": self._current_bucket_index,
            "buckets": self._buckets,
            "length": self._length,
        }

    def add_literal(self, literal: Literal) -> None:
        if self.__contains(literal):
            raise LiteralAlreadyInContextError(literal)
        literal_hash: int = self.__get_hash(literal)
        if literal_hash in self.facts.keys():
            self.facts[literal_hash].append(literal)
        else:
            self.facts[literal_hash] = [literal]
        self._length += 1
        
    def remove_literal(self, literal: Literal) -> None:
        literal_hash: int = self.__get_hash(literal)
        self.facts[literal_hash].remove(literal)
        self._length -= 1

    def unify(self, literal: Literal) -> List[Substitution]: # TODO Make this a generator? Check line 109 in Rule.py...
        """
        Substitution semantics are as follows:
            * [...]: First-order sub;
            * [Substitution()]: Propositional sub (nothing to substitute);
            * None: Failed to unify --> Captured by a LiteralNotInContextError.
        """
        if literal.is_truism():
            return [Substitution()]
        literal_hash: str = self.__get_hash(literal)
        # print("literal hash:", literal_hash)
        # print("literal:", literal)
        # print("self.facts:", [[str(y) for y in x] for x in self.facts.values()])
        if literal_hash not in self.facts.keys():
            raise LiteralNotInContextError(literal)
        # print("hash included")
        subs: List[Substitution] = []
        # print("bucket:", [str(x) for x in self.facts[literal_hash]])
        for fact in self.facts[literal_hash]:
            sub: Union[None, Substitution] = literal.unify(fact)
            # print("sub in context.unify():", sub)
            if sub:
                subs.append(sub)
        # print("subs:", [str(x) for x in subs])
        # subs: List[Substitution] = filter(lambda x: x, [literal.unify(fact) for fact in self.facts[literal_hash]])
        return subs
    
    def remove_conflicts_with(self, ground_facts: Context) -> None:
        for ground_fact in ground_facts:
            negated_hash: int = self.__get_hash(ground_fact, negate = True)
            try:
                bucket: List[Literal] = self.facts[negated_hash]
            except KeyError:
                continue
            n: int = len(bucket)
            i: int = 0
            while i < n:
                fact: Literal = bucket[i]
                if fact.is_conflicting_with(ground_fact):
                    del bucket[i]
                    n -= 1
                else:
                    i += 1
            if len(bucket) == 0:
                del self.facts[negated_hash]

    def __get_hash(self, literal: Literal, negate: bool = False) -> int:
        signature: str = literal.signature
        if negate:
            signature = signature[1:] if signature[0] == "-" else "-" + signature
        return hash(signature)
    
    def __contains(self, literal: Literal) -> bool:
        hash: int = self.__get_hash(literal)
        # # print("hash:", hash)
        try:
            bucket: List[Literal] = self.facts[hash]
        except KeyError:
            return False
        return literal in bucket
    
    def __iter__(self) -> Context:
        self._buckets = list(self.facts.keys())
        return self
    
    def __next__(self) -> Literal:
        if len(self.facts) == 0:
            raise StopIteration
        if self._current_bucket == -1 or self._current_bucket_index == len(self.facts[self._current_bucket]):
            try:
                self._current_bucket = self._buckets.pop()
            except IndexError:
                raise StopIteration
            self._current_bucket_index = 0
        next_literal: Literal = self.facts[self._current_bucket][self._current_bucket_index]
        self._current_bucket_index += 1
        return next_literal
    
    def __len__(self) -> int:
        return self._length
    
    def __str__(self) -> str:
        context_str: str = ""
        for literal in self:
            context_str += str(literal) + "; "
        return context_str
    
    def __contains__(self, literal: Literal) -> bool:
        if not isinstance(literal, Literal): # FIXME It might be useful to also allo for string inputs.
            return False
        return self.__contains(literal)
    
    def __add__(self, other: Context) -> Context:
        copycat: Context = self.__deepcopy__()
        if not isinstance(other, Context):
            raise ValueError("Item of type Context expected. Only contexts can be added with other contexts.")
        for literal in other:
            # # print("literal:", literal)
            try:
                copycat.add_literal(literal)
            except LiteralAlreadyInContextError:
                pass
        return copycat

    def __iadd__(self, other: Context) -> Context:
        if not isinstance(other, Context):
            raise ValueError("Item of type Context expected. Only contexts can be added with other contexts.")
        for literal in other:
            # # print("literal:", literal)
            try:
                self.add_literal(literal)
            except LiteralAlreadyInContextError:
                pass
        return self
    
    def __radd__(self, other: Context) -> Context:
        return self.__add__(other)
    
    def __deepcopy__(self, memodict = {}) -> Context:
        copycat: Context = Context()
        copycat.original_string = self.original_string
        copycat._current_bucket = self._current_bucket
        copycat._current_bucket_index = self._current_bucket_index
        copycat._buckets = self._buckets
        copycat._length = self._length
        for bucket, literals in self.facts.items():
            copycat.facts[bucket] = [deepcopy(x) for x in literals]
        return copycat

    def __eq__(self, __other: object) -> bool:
        if not isinstance(__other, Context):
            return False
        if self._length != __other._length:
            return False
        other_hashkeys = __other.facts.keys()
        for hashkey, literals in self.facts.items():
            if hashkey not in other_hashkeys:
                return False
            other_literals = __other.facts[hashkey]
            for literal in literals:
                if literal not in other_literals:
                    return False
        return True