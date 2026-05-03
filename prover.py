from parser import (
    Predicate, Neg, And, Or, Implies, Forall, Exists, Var, parse
)
from utils import substitute, get_terms, fresh_term, reset_fresh

# Substitution helper

def substitute(formula, var: str, term: str):
    """Replace all free occurrences of variable 'var' with term 'term' in formula."""
    if isinstance(formula, Predicate):
        new_args = tuple(
            Var(term) if a.name == var else a
            for a in formula.args
        )
        return Predicate(formula.name, new_args)

    elif isinstance(formula, Neg):
        return Neg(substitute(formula.formula, var, term))

    elif isinstance(formula, And):
        return And(substitute(formula.left, var, term),
                   substitute(formula.right, var, term))

    elif isinstance(formula, Or):
        return Or(substitute(formula.left, var, term),
                  substitute(formula.right, var, term))

    elif isinstance(formula, Implies):
        return Implies(substitute(formula.left, var, term),
                       substitute(formula.right, var, term))

    elif isinstance(formula, Forall):
        if formula.var == var:
            return formula  # variable is bound, don't substitute inside
        return Forall(formula.var, substitute(formula.formula, var, term))

    elif isinstance(formula, Exists):
        if formula.var == var:
            return formula  # variable is bound, don't substitute inside
        return Exists(formula.var, substitute(formula.formula, var, term))

    return formula

# Term management

def get_terms(left, right):
    """Collect all terms (variable/constant names) appearing in the sequent."""
    terms = set()

    def collect(formula):
        if isinstance(formula, Predicate):
            for a in formula.args:
                terms.add(a.name)
        elif isinstance(formula, (Neg, Forall, Exists)):
            collect(formula.formula)
        elif isinstance(formula, (And, Or, Implies)):
            collect(formula.left)
            collect(formula.right)

    for f in left:
        collect(f)
    for f in right:
        collect(f)

    
    if not terms:
        terms.add('a')
    return terms


_fresh_counter = 0

def fresh_term():
    """Generate a new unique term name."""
    global _fresh_counter
    _fresh_counter += 1
    return f"_t{_fresh_counter}"


def reset_fresh():
    """Reset the fresh term counter (call before each proof attempt)."""
    global _fresh_counter
    _fresh_counter = 0

# Baseline prover: Algorithm 2

def prove_baseline(left: frozenset, right: frozenset, max_depth=5) -> bool:
    """
    Attempt to prove the sequent (left |- right) using Algorithm 2.

    left:      frozenset of formulas (antecedent)
    right:     frozenset of formulas (succedent)
    max_depth: maximum recursion depth (prevents infinite loops)

    Returns True if provable, False otherwise.
    """

    if max_depth <= 0:
        return False

    # Rule id: if any formula appears on both sides -> close branch

    if left & right:
        return True

    # Rule ⊥L: if False (bottom) is in the left -> close branch
    if Predicate('False', ()) in left:
        return True
    # Rule ⊤R: if True (top) is in the right -> close branch
    if Predicate('True', ()) in right:
        return True

    # Single-premise rules on the right (on-branching, priority 1)

    # ¬R: (~A on right) -> (A on left)
    for f in right:
        if isinstance(f, Neg):
            new_left = left | {f.formula}
            new_right = right - {f}
            return prove_baseline(new_left, new_right, max_depth - 1)

    # →R: (A->B on right) -> (A on left, B on right)
    for f in right:
        if isinstance(f, Implies):
            new_left = left | {f.left}
            new_right = (right - {f}) | {f.right}
            return prove_baseline(new_left, new_right, max_depth - 1)

    # ∨R: (A|B on right) -> (A, B on right)
    for f in right:
        if isinstance(f, Or):
            new_right = (right - {f}) | {f.left, f.right}
            return prove_baseline(left, new_right, max_depth - 1)

    # ∀R: (forall x.A on right) -> (A[fresh/x] on right)   [fresh term!]
    for f in right:
        if isinstance(f, Forall):
            t = fresh_term()
            new_formula = substitute(f.formula, f.var, t)
            new_right = (right - {f}) | {new_formula}
            return prove_baseline(left, new_right, max_depth - 1)

    # Single-premise rules on the LEFT (non-branching, priority 1)s
    # ¬L: (~A on left) -> (A on right)
    for f in left:
        if isinstance(f, Neg):
            new_left = left - {f}
            new_right = right | {f.formula}
            return prove_baseline(new_left, new_right, max_depth - 1)

    # ∧L: (A&B on left) -> (A, B on left)
    for f in left:
        if isinstance(f, And):
            new_left = (left - {f}) | {f.left, f.right}
            return prove_baseline(new_left, right, max_depth - 1)

    # ∃L: (exists x.A on left) -> (A[fresh/x] on left)   [fresh term!]
    for f in left:
        if isinstance(f, Exists):
            t = fresh_term()
            new_formula = substitute(f.formula, f.var, t)
            new_left = (left - {f}) | {new_formula}
            return prove_baseline(new_left, right, max_depth - 1)

    # Branching rules (priority 2)

    # ∧R: (A&B on right) -> two branches: (right with A) and (right with B)
    for f in right:
        if isinstance(f, And):
            new_right1 = (right - {f}) | {f.left}
            new_right2 = (right - {f}) | {f.right}
            return (prove_baseline(left, new_right1, max_depth - 1) and
                    prove_baseline(left, new_right2, max_depth - 1))

    # ∨L: (A|B on left) -> two branches: (left with A) and (left with B)
    for f in left:
        if isinstance(f, Or):
            new_left1 = (left - {f}) | {f.left}
            new_left2 = (left - {f}) | {f.right}
            return (prove_baseline(new_left1, right, max_depth - 1) and
                    prove_baseline(new_left2, right, max_depth - 1))

    # →L: (A->B on left) -> two branches
    for f in left:
        if isinstance(f, Implies):
            # Branch 1: prove A (move A to right)
            new_right1 = right | {f.left}
            new_left2 = (left - {f}) | {f.right}
            return (prove_baseline(left - {f}, new_right1, max_depth - 1) and
                    prove_baseline(new_left2, right, max_depth - 1))

    # Quantifier instantiation rules (may loop - use existing terms)
    terms = get_terms(left, right)

    # ∀L: (forall x.A on left) -> keep forall x.A, add A[t/x] for some term t
    for f in left:
        if isinstance(f, Forall):
            for t in terms:
                new_formula = substitute(f.formula, f.var, t)
                if new_formula not in left:  # avoid duplicates
                    new_left = left | {new_formula}
                    if prove_baseline(new_left, right, max_depth - 1):
                        return True
            return False

    # ∃R: (exists x.A on right) -> keep exists x.A, add A[t/x] for some term t
    for f in right:
        if isinstance(f, Exists):
            for t in terms:
                new_formula = substitute(f.formula, f.var, t)
                if new_formula not in right:
                    new_right = right | {new_formula}
                    if prove_baseline(new_right, right, max_depth - 1):
                        return True
            return False

    return False


def check_formula(formula_str: str, max_depth=5) -> bool:
    """Parse and attempt to prove a formula string. Returns True if valid."""
    reset_fresh()
    formula = parse(formula_str)
    return prove_baseline(frozenset(), frozenset({formula}), max_depth)

# Quick test
if __name__ == '__main__':
    test_cases = [
        # (formula, expected_result)
        ("A -> A",                                          True),
        ("A | ~A",                                         True),
        ("~(A & B) -> (~A | ~B)",                         True),
        ("(A -> B) -> ((~A -> B) -> B)",                  True),
        ("A -> (B -> A)",                                  True),
        ("(A & B) -> A",                                   True),
        ("~forall x.R(x) -> exists x.~R(x)",              True),
        ("exists x.forall y.R(x,y) -> forall y.exists x.R(x,y)", True),
        # Invalid formulas (should be False)
        ("A -> B",                                         False),
        ("A & B",                                          False),
        ("forall y.exists x.R(x,y) -> exists x.forall y.R(x,y)", False),
    ]

    print("=== Baseline Prover Test ===\n")
    passed = 0
    for formula, expected in test_cases:
        result = check_formula(formula, max_depth=8)
        status = "PASS" if result == expected else "FAIL"
        validity = "VALID  " if result else "INVALID"
        print(f"  [{status}] {validity} | {formula}")
        if result == expected:
            passed += 1

    print(f"\n  Passed: {passed}/{len(test_cases)}")