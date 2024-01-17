from __future__ import annotations
from typing import List, Tuple
from copy import deepcopy
from prudens_core.entities.Literal import Literal
from prudens_core.entities.Context import Context
from prudens_core.entities.Substitution import Substitution
from prudens_core.parsers.RuleParser import RuleParser, ParsedRule
from prudens_core.errors.RuntimeErrors import LiteralNotInContextError, DuplicateValueError

class Rule:
    __slots__ = ("original_string", "name", "body", "head", "signature")

    def __init__(self, rule_string: str) -> None:
        self.original_string = rule_string
        parser: RuleParser = RuleParser(rule_string)
        try:
            parsed_rule: ParsedRule = parser.parse()
        except Exception as e:
            raise e
        self.name: str = parsed_rule.name
        self.body: List[Literal] = parsed_rule.body # TODO Consider splitting body to distinguish between ? and casual predicates.
        self.head: Literal = parsed_rule.head
        self.signature: str = self.__get_signature()

    def trigger(self, context: Context) -> List[Tuple[Literal, Substitution]]:
        try:
            subs: List[Substitution] = self.__unify(context)
            # print("subs in rule.trigger():", [str(x) for x in subs])
        except LiteralNotInContextError as e:
            raise e
        inferences: List[Literal] = []
        for sub in subs:
            instance: Literal = sub.apply(self.head)
            inferences.append((instance, sub))
        return inferences
    
    def is_triggered(self, context: Context, sub: Substitution) -> bool:
        # FIXME This method should behave as in the following docstring:
        """
        1. Accept `sub` as an argument, which is the sub with which we want to examine the rule.
        2. For each body literal:
            a. Apply the sub to the body literal.
            b. Then quantify unification with context as self.__unify.

        Implementation:
        1. Either as self.__unify (i.e., copy-pasting code and making any changes where needed);
        2. or add a parameter to self.__unify to pass the desired version of the body (beware of deepcopies etc).
        """
        ######################################
        # FIXME YOU ARE HEREEEEEEEEEEEEEEEEE!#
        ######################################
        # FIXME
        # FIXME
        # FIXME
        # FIXME You should not return true but the output of self.__unify()!!! (???)
        # print(f"Rule name: {self.name}\n\tContext: {context}")
        body_instance = [ sub.apply(literal) for literal in self.body ] # sub.apply() deepcopies, so you are fine!
        try:
            unifying_subs = self.__unify(context, body_instance) # FIXME Revisit this. Consider implementing a simple solution?
            # print("subs in rule.trigger():", [str(x) for x in subs])
        except LiteralNotInContextError:
            # print("\t\tFalse")
            return False
        # print("\t\tTrue")
        return bool(unifying_subs)
    
    def instantiate(self, sub: Substitution) -> Rule:
        instance: Rule = Rule(self.original_string)
        for literal in instance.body:
            literal = sub.apply(literal)
        instance.head = sub.apply(instance.head)
        return instance
    
    def is_conflicting_with(self, other: Rule) -> bool:
        # # print(self.head, other.head)
        if not isinstance(other, Rule):
            return False
        if self.head.sign == other.head.sign:
            return False
        main_self_signature: str = self.head.signature if self.head.sign else self.head.signature[1:]
        main_other_signature: str = other.head.signature if other.head.sign else other.head.signature[1:]
        return main_other_signature == main_self_signature

    def __get_signature(self) -> str:
        body_signature: str = "|".join(sorted([x.signature for x in self.body]))
        return body_signature

    def __unify(self, context: Context, body_instance = None) -> List[Substitution]:
        if body_instance == None:
            body_instance = self.body
        initial_sub: Substitution = Substitution()
        current_subs: List[Substitution] = [initial_sub]
        # print("current_subs:", [str(x) for x in current_subs])
        # print("=" * 40)
        for literal in body_instance:
            new_subs: List[Substitution] = [] # FIXME This needs to be a set!
            while current_subs:
                sub: Substitution = current_subs.pop()
                # print("sub before extension:", sub)
                instance: Literal = sub.apply(literal) # TODO Profiling: You are here!
                # print("instance:", instance)
                try:
                    extensions: List[Substitution] = context.unify(instance)
                    # print("extensions:", [str(x) for x in extensions])
                except LiteralNotInContextError as e:
                    raise e
                if not extensions:
                    continue
                # new_subs: List[Substitution] = []
                for extension in extensions:
                    copy_sub: Substitution = deepcopy(sub)
                    try:
                        copy_sub.extend(extension)
                        new_subs.append(copy_sub)
                    except DuplicateValueError:
                        pass
                # print("new_subs:", [str(x) for x in new_subs])
                # print("current_subs:", [str(x) for x in current_subs])
            if new_subs:
                current_subs = new_subs[:]
                # print("EXTENDED current_subs:", [str(x) for x in current_subs])
            else:
                return []
        # print("OUTSIDE of while:", [str(x) for x in  current_subs])
        return current_subs
    
    def __str__(self) -> str:
        rule_str: str = self.name + " :: "
        n: int = len(self.body)
        for i in range(n):
            literal: Literal = self.body[i]
            rule_str += str(literal)
            if i < n - 1:
                rule_str += ", "
        rule_str += " implies " + str(self.head)
        return rule_str