from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class Var:
    """A variable or constant term, e.g. x, y, a, b"""
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Predicate:
    """An atomic formula, e.g. R(x, y) or P(a)"""
    name: str
    args: tuple  # tuple of Var

    def __str__(self):
        if self.args:
            return f"{self.name}({', '.join(str(a) for a in self.args)})"
        return self.name


@dataclass(frozen=True)
class Neg:
    """Negation: ~A"""
    formula: object

    def __str__(self):
        return f"~{self.formula}"


@dataclass(frozen=True)
class And:
    """Conjunction: A & B"""
    left: object
    right: object

    def __str__(self):
        return f"({self.left} & {self.right})"


@dataclass(frozen=True)
class Or:
    """Disjunction: A | B"""
    left: object
    right: object

    def __str__(self):
        return f"({self.left} | {self.right})"


@dataclass(frozen=True)
class Implies:
    """Implication: A -> B"""
    left: object
    right: object

    def __str__(self):
        return f"({self.left} -> {self.right})"


@dataclass(frozen=True)
class Forall:
    """Universal quantifier: forall x.A"""
    var: str
    formula: object

    def __str__(self):
        return f"forall {self.var}.{self.formula}"


@dataclass(frozen=True)
class Exists:
    """Existential quantifier: exists x.A"""
    var: str
    formula: object

    def __str__(self):
        return f"exists {self.var}.{self.formula}"


# Tokeniser


def tokenise(text: str) -> List[str]:
    """Breaks a formula string into a list of tokens."""
    # Normalise unicode symbols to ASCII equivalents
    text = text.replace('¬', '~')
    text = text.replace('∧', '&')
    text = text.replace('∨', '|')
    text = text.replace('→', '->')
    text = text.replace('∀', 'forall ')
    text = text.replace('∃', 'exists ')

    tokens = []
    i = 0
    while i < len(text):
        c = text[i]

        if c.isspace():
            i += 1
            continue

        # Two-character token: ->
        if c == '-' and i + 1 < len(text) and text[i+1] == '>':
            tokens.append('->')
            i += 2
            continue

        # Single character tokens
        if c in ('(', ')', ',', '.', '~', '&', '|'):
            tokens.append(c)
            i += 1
            continue

        # Words: identifiers, keywords (forall, exists), variable names
        if c.isalpha() or c == '_':
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                j += 1
            tokens.append(text[i:j])
            i = j
            continue

        raise ValueError(f"Unexpected character: '{c}' in formula: {text}")

    return tokens

class Parser:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[str]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected: str = None) -> str:
        token = self.peek()
        if token is None:
            raise ValueError(f"Unexpected end of formula, expected '{expected}'")
        if expected and token != expected:
            raise ValueError(f"Expected '{expected}' but got '{token}'")
        self.pos += 1
        return token

    def parse_formula(self):
        """Top-level: handles -> (lowest precedence, right associative)"""
        left = self.parse_or()
        if self.peek() == '->':
            self.consume('->')
            right = self.parse_formula()  # right-associative
            return Implies(left, right)
        return left

    def parse_or(self):
        """Handles |"""
        left = self.parse_and()
        while self.peek() == '|':
            self.consume('|')
            right = self.parse_and()
            left = Or(left, right)
        return left

    def parse_and(self):
        """Handles &"""
        left = self.parse_unary()
        while self.peek() == '&':
            self.consume('&')
            right = self.parse_unary()
            left = And(left, right)
        return left

    def parse_unary(self):
        """Handles ~ (negation) and quantifiers"""
        token = self.peek()

        if token == '~':
            self.consume('~')
            formula = self.parse_unary()
            return Neg(formula)

        if token == 'forall':
            self.consume('forall')
            var = self.consume()  # variable name
            self.consume('.')
            formula = self.parse_unary()
            return Forall(var, formula)

        if token == 'exists':
            self.consume('exists')
            var = self.consume()  # variable name
            self.consume('.')
            formula = self.parse_unary()
            return Exists(var, formula)

        return self.parse_atom()

    def parse_atom(self):
        """Handles predicates like R(x,y) and parenthesised formulas"""
        token = self.peek()

        # Parenthesised formula
        if token == '(':
            self.consume('(')
            formula = self.parse_formula()
            self.consume(')')
            return formula

        # Predicate: Name possibly followed by (args)
        if token and token[0].isupper():
            name = self.consume()
            if self.peek() == '(':
                self.consume('(')
                args = [Var(self.consume())]
                while self.peek() == ',':
                    self.consume(',')
                    args.append(Var(self.consume()))
                self.consume(')')
                return Predicate(name, tuple(args))
            return Predicate(name, ())

        # Propositional variable (uppercase single letter treated as predicate)
        if token and token.isalpha():
            name = self.consume()
            if name[0].isupper():
                return Predicate(name, ())
            # lowercase with no parens = propositional atom (treat as 0-ary predicate)
            return Predicate(name, ())

        raise ValueError(f"Unexpected token '{token}' while parsing atom")


def parse(text: str):
    """Parse a single formula string and return the formula object."""
    tokens = tokenise(text.strip())
    parser = Parser(tokens)
    formula = parser.parse_formula()
    if parser.peek() is not None:
        raise ValueError(f"Unexpected leftover tokens: {parser.tokens[parser.pos:]}")
    return formula


def parse_file(filepath: str) -> List:
    """
    Read a file where each non-empty line is one formula.
    Returns a list of parsed formula objects.
    """
    formulas = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # skip blank lines and comments
                continue
            try:
                formula = parse(line)
                formulas.append(formula)
            except ValueError as e:
                print(f"  [Line {lineno}] Parse error: {e}")
    return formulas

if __name__ == '__main__':
    test_formulas = [
        "~forall x.R(x) -> exists x.~R(x)",
        "forall x.R1(x) -> (forall x.R2(x) -> forall y.(R1(y) & R2(y)))",
        "exists x.forall y.R(x,y) -> forall y.exists x.R(x,y)",
        "A -> (B -> A)",
        "(A -> B) -> ((~A -> B) -> B)",
        "A | ~A",
        "~(A & B) -> (~A | ~B)",
    ]

    print("=== Parser Test ===\n")
    for f in test_formulas:
        parsed = parse(f)
        print(f"  Input : {f}")
        print(f"  Parsed: {parsed}")
        print()
