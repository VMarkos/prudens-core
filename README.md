# README

Some (really) brief documentation of the python version of Prudens.

## Using Prudens

To use Prudens, just clone this repo to the location you want and import any required functionality. The most useful constructs offerred by Prudens are:
* **Policies**, available through `prudens_core.entities.Policy`, and;
* **Contexts**, available through `prudens_core.entities.Context`.

For instance, a simple example might be as follows (also available at [main.py](https://github.com/VMarkos/prudens-core/blob/main/main.py)):

```python
from prudens_core.entities.Policy import Policy
from prudens_core.entities.Context import Context

context_str = "bird(alice); bird(bob); bird(charlie); penguin(alice); penguin(bob); super(alice);"
policy_str = """@Policy
    R1 :: bird(X) implies flies(X);
    R2 :: penguin(X) implies -flies(X);
    R3 :: super(X) implies flies(X);
    
    @Priorities
    R2 > R1;
    R3 > R2;
"""

policy = Policy(policy_str)
context = Context(context_str)
policy.infer(context)
print("Inferences:", str(policy.inferences))
```

Here, we define a simple policy that helps a machine understand which birds can fly and which can't. Namely:
* Birds, in general, fly (`R1`);
* Penguins, in general, do not fly (`R2`);
* Super birds (and super penguins, in particular), do fly (`R3`).

With those in mind, a context like the one provided above:

```
bird(alice); bird(bob); bird(charlie); penguin(alice); penguin(bob); super(alice);
```

results to the following set of inferences (we omit context facts for brevity):

```
-flies(bob); flies(charlie); flies(alice);
```

## Prudens Syntax

There are two key construct in Prudens:
* **Policies**, which consist of all the rules and meta-rule information that describe the global knowledge of an agent about a certain range of topics, and;
* **Contexts**, which consists of indisputable facts that an agent is aware of (e.g., by observing / sensing its environment).

We shall describe Prudens syntax in a top-down manner, starting from the highest-level constructs, moving towards the lowest-level ones.

### Policy Syntax

All policies should have the following abstract structure:

```
@Policy
<Rules>

@Priorities
<Priorities>
```

The two `@` directives, `@Policy` and `@Priorities` indicate where the main policy and prioritization content begins, respectively. This syntax is order-sensitive, meaning that including `@Priorities` prior to introducing rules is not allowed.

Regarding rules in a policy, they are introduced below the `@Policy` directive and are delimited by a semicolon \(`;`\). The only case where the delimiting semicolon can be omiting is in the case of the last rule in a policy. Similarly, priorities are declared under the `@Priorities` directive and are delimited again by a semicolon (`;`). As with rules, the last priority declared need not be followed by a semicolon (nevertheless, this is not considered as a syntax error at the moment).

### Rule Syntax

Rules have the following abstract syntax:

```
<Rule name> :: <literal1>, <literal2>, ..., <literalN> implies <head literal>
```

So, a rule is split into three main parts:
* its **name**, which corresponds to the part left of the double double dots (`::`);
* its **body**, which is enclosed between the double double dots (`::`) and the reserved `implies` keywords, and;
* its **head**, which follows the `implies` keyword.

Regarding a rule's name, it can be any string starting with a lower- or capital-case letter of the lating alphabet, `[a-zA-Z]`, followed by zero or more alphanumeric characters or underscores, `[a-zA-Z0-9_]`. Thus, valid rule names can be `rule1`, `Rule_1`, or `R15_a` but not `_rule` (because it starts with an underscore), `3Rule` (because it starts with a digit) or `rule#1` (because it contains a non-alphanumeric or underscore symbol).

A rule's body is a comma-separated list of literals (see below for literal syntax).

### Literal Syntax

### Priority Syntax

### Context Syntax

## Unit Testing

\[coming soon\]

## Documentation

\[coming soon\]
