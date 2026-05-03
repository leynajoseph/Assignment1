from parser import (
    Predicate, Neg, And, Or, Implies, Forall, Exists, Var, parse
)
from utils import substitute, get_terms, fresh_term, reset_fresh

# Improved prover core

def prove_improved(left: frozenset, right: frozenset,
                   depth: int, max_depth: int,
                   visited: frozenset) -> bool:
    """
    Attempt to prove sequent (left |- right).

    Improvements applied:
      - Loop detection: check visited set before expanding
      - Depth limit: stop if depth exceeded
      - Smart rule ordering: close > non-branch > branch > quantifiers
    """

    # Improvement 2: Loop detection
    sequent = (left, right)
    if sequent in visited:
        return False
    visited = visited | {sequent}  # immutable update for this branch

    # Improvement 1: Depth limit
    if depth > max_depth:
        return False

    # Priority 1: Closing rules (fastest, try first)

    # Rule id: formula appears on both sides
    if left & right:
        return True

    # Rule False-L: False on left
    if Predicate('False', ()) in left:
        return True

    # Rule True-R: True on right
    if Predicate('True', ()) in right:
        return True
    
    # Priority 2: Non-branching rules on RIGHT (single premise)
    # Improvement 3: these are tried before branching rules

    # ~R: ~A on right -> A moves to left
    for f in right:
        if isinstance(f, Neg):
            new_left = left | {f.formula}
            new_right = right - {f}
            return prove_improved(new_left, new_right, depth + 1, max_depth, visited)

    # ->R: A->B on right -> A to left, B stays right
    for f in right:
        if isinstance(f, Implies):
            new_left = left | {f.left}
            new_right = (right - {f}) | {f.right}
            return prove_improved(new_left, new_right, depth + 1, max_depth, visited)

    # vR: A|B on right -> A and B both on right
    for f in right:
        if isinstance(f, Or):
            new_right = (right - {f}) | {f.left, f.right}
            return prove_improved(left, new_right, depth + 1, max_depth, visited)

    # forall R: forall x.A on right -> A[fresh/x] on right
    for f in right:
        if isinstance(f, Forall):
            t = fresh_term()
            new_formula = substitute(f.formula, f.var, t)
            new_right = (right - {f}) | {new_formula}
            return prove_improved(left, new_right, depth + 1, max_depth, visited)

    # Priority 2: Non-branching rules on LEFT (single premise)
    # ------------------------------------------------------------------
    # ~L: ~A on left -> A moves to right
    for f in left:
        if isinstance(f, Neg):
            new_left = left - {f}
            new_right = right | {f.formula}
            return prove_improved(new_left, new_right, depth + 1, max_depth, visited)

    # &L: A&B on left -> A and B both on left
    for f in left:
        if isinstance(f, And):
            new_left = (left - {f}) | {f.left, f.right}
            return prove_improved(new_left, right, depth + 1, max_depth, visited)

    # exists L: exists x.A on left -> A[fresh/x] on left
    for f in left:
        if isinstance(f, Exists):
            t = fresh_term()
            new_formula = substitute(f.formula, f.var, t)
            new_left = (left - {f}) | {new_formula}
            return prove_improved(new_left, right, depth + 1, max_depth, visited)

    # ------------------------------------------------------------------
    # Priority 3: Branching rules (two premises)
    # Improvement 3: these are tried after all single-premise rules
    # ------------------------------------------------------------------

    # &R: A&B on right -> prove A and prove B separately
    for f in right:
        if isinstance(f, And):
            new_right1 = (right - {f}) | {f.left}
            new_right2 = (right - {f}) | {f.right}
            return (prove_improved(left, new_right1, depth + 1, max_depth, visited) and
                    prove_improved(left, new_right2, depth + 1, max_depth, visited))

    # vL: A|B on left -> prove with A and prove with B separately
    for f in left:
        if isinstance(f, Or):
            new_left1 = (left - {f}) | {f.left}
            new_left2 = (left - {f}) | {f.right}
            return (prove_improved(new_left1, right, depth + 1, max_depth, visited) and
                    prove_improved(new_left2, right, depth + 1, max_depth, visited))

    # ->L: A->B on left -> two branches
    for f in left:
        if isinstance(f, Implies):
            new_right1 = right | {f.left}
            new_left2 = (left - {f}) | {f.right}
            return (prove_improved(left - {f}, new_right1, depth + 1, max_depth, visited) and
                    prove_improved(new_left2, right, depth + 1, max_depth, visited))

    # Priority 4: Quantifier instantiation (potential loops)
    # Improvement 2 (loop detection) protects us here
    terms = get_terms(left, right)

    # forall L: keep forall x.A, add A[t/x] for existing terms
    for f in left:
        if isinstance(f, Forall):
            for t in terms:
                new_formula = substitute(f.formula, f.var, t)
                if new_formula not in left:
                    new_left = left | {new_formula}
                    if prove_improved(new_left, right, depth + 1, max_depth, visited):
                        return True
            return False

    # exists R: keep exists x.A, add A[t/x] for existing terms
    for f in right:
        if isinstance(f, Exists):
            for t in terms:
                new_formula = substitute(f.formula, f.var, t)
                if new_formula not in right:
                    new_right = right | {new_formula}
                    if prove_improved(left, new_right, depth + 1, max_depth, visited):
                        return True
            # also try a fresh term if existing terms didn't work
            t = fresh_term()
            new_formula = substitute(f.formula, f.var, t)
            new_right = right | {new_formula}
            if prove_improved(left, new_right, depth + 1, max_depth, visited):
                return True
            return False

    return False

# Improvement 1: Iterative deepening wrapper

def prove_iterative_deepening(left: frozenset, right: frozenset,
                               max_depth=15) -> bool:
    """
    Try proving the sequent at increasing depths 1, 2, 3, ..., max_depth.
    Combined with loop detection and smart rule ordering, this finds proofs
    at the shallowest depth possible without missing valid proofs.
    """
    for depth_limit in range(1, max_depth + 1):
        reset_fresh()
        if prove_improved(left, right, depth=0,
                          max_depth=depth_limit,
                          visited=frozenset()):
            return True
    return False


def check_formula(formula_str: str, max_depth=10) -> bool:
    """Parse and attempt to prove a formula string. Returns True if valid."""
    formula = parse(formula_str)
    return prove_iterative_deepening(
        frozenset(), frozenset({formula}), max_depth
    )

# Quick test

if __name__ == '__main__':
    test_cases = [
        ("A -> A",                                                    True),
        ("A | ~A",                                                    True),
        ("~(A & B) -> (~A | ~B)",                                    True),
        ("(A -> B) -> ((~A -> B) -> B)",                             True),
        ("A -> (B -> A)",                                             True),
        ("(A & B) -> A",                                              True),
        ("~forall x.R(x) -> exists x.~R(x)",                        True),
        ("exists x.forall y.R(x,y) -> forall y.exists x.R(x,y)",    True),
        # Invalid
        ("A -> B",                                                    False),
        ("A & B",                                                     False),
        ("forall y.exists x.R(x,y) -> exists x.forall y.R(x,y)",    False),
    ]

    print("=== Improved Prover Test ===\n")
    passed = 0
    for formula, expected in test_cases:
        result = check_formula(formula, max_depth=10)
        status = "PASS" if result == expected else "FAIL"
        validity = "VALID  " if result else "INVALID"
        print(f"  [{status}] {validity} | {formula}")
        if result == expected:
            passed += 1

    print(f"\n  Passed: {passed}/{len(test_cases)}")