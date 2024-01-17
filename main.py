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