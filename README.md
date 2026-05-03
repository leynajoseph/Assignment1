# 3806ICT Assignment 1 — Automated Reasoning Prover

Implementation and improvement of Algorithm 2 (Page 67 of *Fundamentals of Logic and Computation* by Hou, 2021) for backward proof search in first-order logic using the LK* sequent calculus.

This repository contains both the **baseline** prover (a faithful implementation of Algorithm 2) and an **improved** prover that adds three enhancements: iterative deepening, loop/cycle detection, and smart rule ordering.

## Repository structure

```
.
├── parser.py                       # Tokeniser + recursive-descent parser
├── utils.py                        # Substitution, term collection, fresh terms
├── prover.py                       # Baseline Algorithm 2
├── improved_prover.py              # Improved version with three enhancements
├── benchmark.py                    # Runs both provers on all datasets
├── visualise.py                    # Generates result charts (vector PDF)
├── make_architecture_diagram.py    # Generates the system architecture figure
├── datasets/
│   ├── textbook.txt                # Examples adapted from the course textbook
│   ├── pelletier.txt               # Subset of the Pelletier (1986) benchmark
│   └── generated.txt               # Programmatically generated formulas
└── results/
    ├── results.csv                 # Per-formula benchmark output
    ├── chart_overall.pdf           # Overall solved-count chart
    ├── chart_solved_counts.pdf     # Per-dataset solved counts
    ├── chart_solve_percent.pdf     # Per-dataset solve rates
    └── architecture_diagram.pdf    # System architecture figure
```

## Requirements

- Python 3.8 or higher
- `matplotlib` (only for chart generation)

```bash
pip install matplotlib
```

## How to run

Run the full benchmark pipeline:

```bash
python3 benchmark.py
```

Generate the result charts (after running the benchmark):

```bash
python3 visualise.py
```

Generate the architecture diagram:

```bash
python3 make_architecture_diagram.py
```

## Formula syntax

Each line in a dataset file uses the following syntax:

| Symbol  | Operator              |
|---------|-----------------------|
| `~`     | negation              |
| `&`     | conjunction           |
| `\|`     | disjunction           |
| `->`    | implication           |
| `forall x.A` | universal quantifier |
| `exists x.A` | existential quantifier |
| `R(x,y)` | predicate / relation |

Each non-comment line in a dataset file has the form:

```
VALID   | <formula>
INVALID | <formula>
```

## Improvements over the baseline

| # | Improvement | Purpose |
|---|-------------|---------|
| 1 | Iterative deepening | Prevents non-termination by gradually expanding the search depth |
| 2 | Loop / cycle detection | Stops the search early if the same sequent is revisited |
| 3 | Smart rule ordering | Closing rules > non-branching rules > branching rules > quantifier instantiation |

## Data sources

- **Textbook formulas:** Hou, Z. (2021). *Fundamentals of Logic and Computation: With Practical Automated Reasoning and Verification.* Springer.
- **Pelletier problems:** Pelletier, F. J. (1986). Seventy-five problems for testing automatic theorem provers. *Journal of Automated Reasoning, 2*(2), 191–216.
- **Generated formulas:** Constructed locally from known logical templates of guaranteed validity / invalidity.

## Author

Leyna Joseph — 3806ICT Logic and Automated Reasoning, Trimester 1, 2026.
