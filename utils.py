from parser import Predicate, Neg, And, Or, Implies, Forall, Exists, Var

def substitute(formula, var: str, term: str):
    """Replace all free occurrences of variable 'var' with term in formula."""
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
            return formula
        return Forall(formula.var, substitute(formula.formula, var, term))
    elif isinstance(formula, Exists):
        if formula.var == var:
            return formula
        return Exists(formula.var, substitute(formula.formula, var, term))
    return formula

# Term management

def get_terms(left, right):
    """Collect all term names appearing in the sequent."""
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
    """Reset the fresh term counter."""
    global _fresh_counter
    _fresh_counter = 0