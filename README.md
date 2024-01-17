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
* Penguins, in general, do not fly (`R2`) and this is an exception to `R1` (this is captured by `R2 > R1`);
* Super birds (and super penguins, in particular), do fly (`R3`) and this is an exception to `R2` (this is captured by `R3 > R2`).

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

A rule's body is a comma-separated list of literals (see below for literal syntax). Rule bodies cannot be empty, i.e., each rule must have at least one literal in its body, even if it is only the trivially true literal `true` \(this literal is always true, as if it is present in any context\).

Finally, a rule's head is just a literal. It is important to note that each rule must have exaclty one head literal, so, no commas or other irrelevant characters may appear in rule heads.

### Literal Syntax

There are two kinds of literals in Prudens (which can be thought of as one kind, but more on that later):
* **propositional** literals, which are essentially just propositional variables or their negation, and;
* **relational** literals, which are relational (i.e., first order) predicates or their negation.

Propositional literals correspond to facts, conditions, or other meaningful entities of the universe of discource. They are declared as strings starting with a **lower-case** letter of the latin alphabet followed by zero or more alphanumerical characters or underscores. For instrance, `rains`, `isRaining`, and `on_day_3` are some valid propositional literal examples. Any such literals are called **positive** literals, because they refer to facts and conditions that hold in a given context. To negate them, one can use a single dash, (`-`). So, `-rains` is the logically opposite of `rains`. **Beware!** Negation in Prudens, in contrast with Prolog and other similar reasoning engines, is treated as **classical negation.** That is, not having observed `rains` is not the same as `-rains`. So, for each literal one can distinguish between three states:
* a positive literal has been observed / inferred (i.e., it is part of a context or has been inferred during the reasoning process), e.g. `rains`;
* the negation of the literal has been observed / inferred (i.e., it is part of a context or has been inferred during the reasoning process), e.g. `-rains`;
* neither a positive nor a negative instance of a literal have been observed, i.e., we do not know whether it is raining (`rains`) or not (`-rains`) at the moment, which means that the corresponding fact is essentially **unobserved.**

The above is important to bear in mind when writing / debugging Prudens policies.

Apart from propositional literals, Prudens also offers relational literals, which correspond to relations between entities of our universe of discourse. As such, relational literals can take arguments, corresponding to their **arity**, i.e., the number of different entities (arguments) that are related through a certain literal. For instance, `parentOf(alice, bob)`, with the intended interpretation that `bob` is the parent of `alice` is a binary relations (`arity = 2` in that case). Relational literals have two syntactic components:
* their **name**, which adheres to the same restrictions as a propositional literal, i.e., it is declared as a string starting with a **lower-case** letter of the latin alphabet followed by zero or more alphanumerical characters or underscores, and;
* their **arguments list**, which is a comma-separated list of at least one variable or constant (it may well contain both variables and constants) enclosed in parentheses.

Constants are syntactically identical to propositional literals and correspond to entities of our universe of discourse. So, in the above, `alice` and `bob` are constants corresponding to two (presumably distinct) entities (probably named as "Alice" and "Bob"). However, the real power of relational syntax comes from the ability to introduce variables in place of actual constants. That is, in order to discribe the abstract notion of "someone is the parent of Alice", one could simple write:

```
parentOf(alice, X)
```

In this case, `X` is a **variable**, i.e., a placeholder for some actual entity that can, at any time, take its place. Syntactically, variables are identical to constants except for they have to start with an **upper-case** letter of the latin alphabet. So, `X`, `Someone`, `X_2`, and `This_is_a_variable_0` are all valid variables in Prudens.

### Priority Syntax

Priorities are used to indicate which rule should be considered in case of conflicts. For instance, consider in the simple bird example we had above:

```
@Policy
R1 :: bird(X) implies flies(X);
R2 :: penguin(X) implies -flies(X);
R3 :: super(X) implies flies(X);

@Priorities
R2 > R1;
R3 > R2;
```

In this example, we declare under the `@Priorities` directive that `R2 > R1`, which means that `R2` is considered of higher priority than `R1` whenever they lead to conflicting inferences. So, whenever both rules are triggered with the same value of `X`, Prudens will keep the inference of `R2` over that of `R1`. Similarly, Prudens prefers `R3` over `R2` whenever they lead to some conflict.

In order to simplify things, one can also use the `deafult` keyword to indicate that rule priorities should be inferred by order of appearance, i.e., the lower a rule appears, the higher its priority over conflicting ones. So, the above would be equivalent to this shorter version:

```
@Policy
R1 :: bird(X) implies flies(X);
R2 :: penguin(X) implies -flies(X);
R3 :: super(X) implies flies(X);

@Priorities
default
```

At last, observe that one need not determine priorities between all conflicting rules, which means that the following policy is 100% valid:

```
@Policy
R1 :: bird(X) implies flies(X);
R2 :: penguin(X) implies -flies(X);
R3 :: super(X) implies flies(X);

@Priorities
R3 > R2;
```

Essentially, this means that whenever `R2` and `R3` lead to a conflicting inference, Prudens preferes the latter, however, when `R1` and `R2` lead to a conflict Prudens does not know what to do, resulting to a dilemma (more on that in the corresponding section). Also, the following is an (extremely rare but) syntactically valid Prudens policy, in which all conflicts raise dilemmas:

```
@Policy
R1 :: bird(X) implies flies(X);
R2 :: penguin(X) implies -flies(X);
R3 :: super(X) implies flies(X);

@Priorities;
```

### Context Syntax

Contexts correspond to lists of facts that are indisputably true (e.g., they have been observed from the environment). They are simply semicolon (`;`) separated lists of **grounded** literals. As with policies, the last literal of a context need not be followed by a semicolon. So, a valid context might be as follows:

```
bird(alice); bird(bob); bird(charlie); penguin(alice); penguin(bob); super(alice);
```

*Side note: One can also have ungrounded literals in contexts, but in such cases, absurd things may happen, due to the way Prudens unifies variables and the scope of each rule within the same policy. More on that in the corresponding section*

## Unit Testing

\[coming soon\]

## Documentation

\[coming soon\]

## Appendix A: Instructing a Self-Driving Car

A few draft notes on a dummy Prudens policy for a self-driving car.

### In Free Text

First we present the policy in free text.

* Stay in your lane forever.
* In case you want to turn (left or right), use your left / right alarms about 100 metres before turning.
* If you are on a highway and want to turn, then use your alarms about 500 metres before turning.
* Respect speed limits.
* If it is night, be extra cautious and run at 80% of speed limits.
* If the driver has informed you that there is an emergency, top speed limits (day and night).
* Slow down on yellow lights with the intention to eventually stop.
* In case of emergency do not slow down on yellow lights.
* Change lanes about 1km before you need to take a turn.
* Do not change lanes frequently, where frequently means more often than once per minute.

Do not use the above policy in realistic scenarios, more probably than not, you will end up crashed on a wall!

### In Prudens CNLI

* Always stay in your lane.
* If you want to turn at a turn towards a direction and you are about 100 metres before that turn then turn on alarms towards that direction.
* If you are on highway and you want to turn at a turn towards a direction and you are about 500 metres before that turn then turn on alarms towards that direction.

\[coming soon\]

### In Prudens

Predicates used:

| Predicate | Interpretation |
| --- | --- |
| `!changeLane(D)` | Change lane towards direction `D` |
| `location(O, Lon, Lat)` | Object `O` is located at longtitude `Lon` and latitude `Lat` |
| `?geoDist(Lon1, Lat1, Lon2, Lat2, D)` | Locations (`Lon1`,`Lat1`) and (`Lon2`,`Lat2`) have a distance `D` (haversine distance) |
| `selfDist(O, D)` | Object `O` has distance `D` from self |
| `?lt(X, Y)` | `X` < `Y` |
| `about(X, Y)` | `X` is about equal to `Y` |
| `intentionToTurn(T, D)` | I want to turn at turn `T` to direction `D` |
| `drivingOn(R)` | Driving on road of type `R` |
| `!turnOnAlarms(D)` | Turn on alarms towards direction `D` |
| `speedLimit(S)` | Speed limit is `S` km/h |
| `curentSpeed(S)` | Current speed is `S` km/h |
| `!slowDown` | Slow down |
| `!speedUp` | Speed up |
| `time(H,M,S)` | Time is `H:M:S` in hour:minute:second format |
| `night` | It is night |
| `emergency` | There is an emergency |
| `roughlyAtSpeedLimit(S)` | Almost equal to speed limit `S` |
| `trafficLight(C)` | Traffic light of colour `C` |
| `!stopAfterHours(H)` | Stop car after `H` hours |
| `lastLaneChangeTS(H,M,S)` | Last lane change timestamp is `H`:`M`:`S` in hour:minute:second format |
| `frequentLaneChange` | There is an intention for too frequent lane changes |

To translate rule "Stay in your lane forever" we can write the following rule:

```
R0 ::  implies -!changeLane(left);
R1 ::  implies -!changeLane(right);
```

To translate rule "In case you want to turn (left or right), use your left / right alarms for at least 100 metres before turning"
we can use the following rule:

```
D1 :: location(self, SLon, SLat), location(Target, TLon, TLat) ?geoDist(SLon, SLat, TLon, TLat, Distance) implies selfDist(Target, Distance);
D2 :: selfDist(Target, Dist), ?lt(100, Dist), ?lt(Dist, 110) implies about(Target, 100);
R2 :: intentionToTurn(Turn, Direction), about(Turn, 100) implies !turnOnAlarms(Direction);
```

Here we have used two auxiliary rules to define the concept of "distance from self" and "about 100 meters away". With the help of those, R2 is
pretty much straightforward. Similarly, rule "If you are on a highway and want to turn, then use your alarms about 500 metres before turning"
can be expressed as follows:

```
D3 :: selfDist(Target, Dist), ?lt(500, Dist), ?lt(Dist, 550) implies about(Target, 500);
R3 :: intentionToTurn(Turn, Direction), about(Turn, 500), drivingOn(highway) implies !turnOnAlarms(Direction);
```

In this case, R3 will be triggered before R2 and thus, we have to take care not to repeat the same action (which would do nothing in this case).

Regarding rule "Respect speed limits" we can use the following:

```
R4 :: speedLimit(L), currentSpeed(S), ?lt(L, S) implies !slowDown;
```

Essentially, the above rule is triggered while our current speed is larger than the speed limit (we assume that the car consults this policy repeatedly and makes decisions based on it).

For the next rule, "If it is night, be extra cautious and run at 80% of speed limits", we can use the following:

```
D4 :: time(H,M,S), ?lt(H, 8) implies night;
D5 :: time(H,M,S), ?lt(19, H) implies night;
R5 :: night, speedLimit(L), currentSpeed(S), ?lt(L, 0.8 * S) imlies !slowDown;
```

We first define as night the time interval between 20:00 and 8:00 (next day), which is a bit arbitrary but suffices for our purposes. Then, we describe the conditions under which one should slow down to 80% of the current speed limit. Observe that, as befor, we need not introduce any conflicts since we just specify further the occasions on which the car should slow down.

For rule "If the driver has informed you that there is an emergency, top speed limits (day and night)" we can use:

```
R6 :: emergency, speedLimit(L), currentSpeed(S), ?lt(S, L) implies !speedUp;

C1 :: !speedUp # !slowDown;
```

With the above we declare a condition under which we should speed up (in case of emergency) and we also make it explicit that the two actions (!speedUp and !slowDown) are conflicting (through Rule C1). Since we have introduced a conflict we know how to resolve, we also need to inlcude the following prioritisation:

```
R6 > R5;
R4 > R6;
```

Observe that R6 being prior to R5 means that in case it is night we will not slow down to the 80% of the speed limit while R4 being prior to R6 means that we will always keep ourselve below the speed limit.

However ,this is a bit unrealistic. Imagine a car running close to the speed limit of 100 km/h in an emergency situation. Once it reaches 100.01 km/h it will start slowing down due to R4. Once it hits 99.98 km/h it will start speeding up since now only R6 is triggered (at day; at night, it beats R5), which may temporarily lead to a speed above 100 km/h, resulting to an endless slow-down -- speed-up loop. Evidently, we should somehow allow for some padding in our restrictions, to 
make sure that the above does not occur.

On simple way is to just soften R6 as follows:

```
R7 :: emergency, speedLimit(L), currentSpeed(S), ?lt(S, 0.99 * L) implies !speedUp;
```

Strictly speaking, this is not what the NL policy describes, but thus we make sure that speeding up stops a bit before we reach the speed limit, thus reducing the chance of starting to slow down (evidently, 0.99 above is arbutrary and a more expert designer could make a more informed choice).

Another way would be to define a notion of "roughly at the speed limit", as follows:

```
D6 :: speedLimit(L), currentSpeed(S), ?lt(S, 1.02 * L), ?lt(0.98 * L, S) implies roughlyAtSpeedLimit(S);
```

Then, we could introduce the following rules:

```
R7 :: currentSpeed(S), roughlyAtSpeedLimit(S) implies -!slowDown
R8 :: currentSpeed(S), roughlyAtSpeedLimit(S) implies -!speedUp;
```

And priorities:

```
R7 > R4;
R7 > R5;
R8 > R6;
```

Thus, once we are 2% close to the speed limit, we perform no action (we could make this one-sided, to make sure we are always absolutely respecting the speed limit).

Back to the rest of the policy, for rule "Slow down on yellow lights with the intention to eventually stop" we can use:

```
R9 :: trafficLight(yellow) implies !slowDown;
R10 :: trafficLight(yellow), selfDist(trafficLight, D), currentSpeed(S), ?=(H, D / S) implies !stopAfterHours(H);
```

We also introduce priorities:

```
R9 > R6;
```

R9 essentially informs us that we should start slowing down, while R10 computes in how much time we should have stopped (in hours, a bit impractical, but, this is just a demo). Also, prioritising R9 over R6 means that we should
respect traffic lights even in cases of emergency. This is an interesting point, since it might be the case that 
the emergency we are dealing with is way more important than a yellow light (e.g., when we transfer a pregnant woman
and need to arrive as soon as possible to the hospital). To illustrate that this is a case where human intervention is required, we can not include `R9 > R6` and allow the (human) driver make a decision (since, a dilemma will be raised in case both rules are triggered).

All the above are (luckily) resolved for us, since the next rule we have to deal with is: "In case of emergency do not slow down on yellow lights". To do so, we introduce:

```
R11 :: emergency, trafficLight(yellow) implies -!slowDown;
```

Also, the corresponding prioritisation:

```
R11 > R9;
R11 > R7;
R11 > R5;
```

Next, rule "Change lanes about 1km before you need to take a turn" can be expressed through:

```
R12 :: intentionToTurn(Turn, Direction), selfDist(Turn, D), ?lt(D, 1000) implies !changeLane(Direction);
```

There's an issue with the above. Once we approach the target turn at a 1km distance, we will always infer that we should changeLane. However, this is not a viable solution; we have to change lane just as many times as possible. Thus, we improve R11 by introducing a relevant predicate than informs us whether we can actually change lane towards a certain direction.

```
R13 :: intentionToTurn(Turn, Direction), selfDist(Turn, D), ?lt(D, 1000), canChangeLane(Direction) implies !changeLane(Direction);
```

Also, we add priorities:

```
R13 > R0;
R13 > R1;
```

Now, to express our last rule, "Do not change lanes frequently, where frequently means more often than once per minute", we need first to define what frequently means:

```
D7 :: lastLaneChangeTS(H1, M1, S1), time(H2, M2, S2), ?lt(1, abs(M2 - M1)) implies frequentLaneChange;
```

Given that, we can prohibit frequent lane changes as follows:

```
R12 :: frequentLaneChange implies -!changeLane(left);
R13 :: frequentLaneChange implies -!changeLane(right);
```

We can choose not to add priorities here, to ask for human intervention, since it might be the case that we have missed an important turn, thus we should change multiple lanes at the same time. Moreover, we might need to change two lanes to the same direction to prepare for an upcoming turn, in which case we should / could that in less than a minute.

While not exhaustive, this example demonstrates the key features of Prudens at its current state. The policy in its entireity is shown below:

```
@Policy
D1 :: location(self, SLon, SLat), location(Target, TLon, TLat) ?geoDist(SLon, SLat, TLon, TLat, Distance) implies selfDist(Target, Distance);
D2 :: selfDist(Target, Dist), ?lt(100, Dist), ?lt(Dist, 110) implies about(Target, 100);
D3 :: selfDist(Target, Dist), ?lt(500, Dist), ?lt(Dist, 550) implies about(Target, 500);
D4 :: time(H,M,S), ?lt(H, 8) implies night;
D5 :: time(H,M,S), ?lt(19, H) implies night;
D6 :: speedLimit(L), currentSpeed(S), ?lt(S, 1.02 * L), ?lt(0.98 * L, S) implies roughlyAtSpeedLimit(S);
D6 :: lastLaneChangeTS(H1, M1, S1), time(H2, M2, S2), ?lt(1, abs(M2 - M1)) implies frequentLaneChange;

R0 ::  implies -!changeLane(left);
R1 ::  implies -!changeLane(right);
R2 :: intentionToTurn(Turn, Direction), about(Turn, 100) implies !turnOnAlarms(Direction);
R3 :: intentionToTurn(Turn, Direction), about(Turn, 500), drivingOn(highway) implies !turnOnAlarms(Direction);
R4 :: speedLimit(L), currentSpeed(S), ?lt(L, S) implies !slowDown;
R5 :: night, speedLimit(L), currentSpeed(S), ?lt(L, 0.8 * S) imlies !slowDown;
R6 :: emergency, speedLimit(L), currentSpeed(S), ?lt(S, L) implies !speedUp;
R7 :: currentSpeed(S), roughlyAtSpeedLimit(S) implies -!slowDown
R8 :: currentSpeed(S), roughlyAtSpeedLimit(S) implies -!speedUp;
R9 :: trafficLight(yellow) implies !slowDown;
R10 :: trafficLight(yellow), selfDist(trafficLight, D), currentSpeed(S), ?=(H, D / S) implies !stopAfterHours(H);
R11 :: emergency, trafficLight(yellow) implies -!slowDown;
R12 :: intentionToTurn(Turn, Direction), selfDist(Turn, D), ?lt(D, 1000) implies !changeLane(Direction);
R13 :: intentionToTurn(Turn, Direction), selfDist(Turn, D), ?lt(D, 1000), canChangeLane(Direction) implies !changeLane(Direction);
R12 :: frequentLaneChange implies -!changeLane(left);
R13 :: frequentLaneChange implies -!changeLane(right);

@Conflicts
C1 :: !speedUp # !slowDown;

@Priorities
R6 > R5;
R4 > R6;
R7 > R4;
R7 > R5;
R8 > R6;
R9 > R6;
R11 > R9;
R11 > R7;
R11 > R5;
R13 > R0;
R13 > R1;
```
