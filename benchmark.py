import time
import csv
import os
import signal

from parser import parse
from prover import prove_baseline
from improved_prover import prove_iterative_deepening
from utils import reset_fresh

# Timeout handling

class TimeoutErr(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutErr("Formula timed out")


def run_with_timeout(func, timeout_sec):
    """Run a function with a timeout. Returns (result, elapsed, timed_out)."""
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout_sec)
    start = time.perf_counter()
    try:
        result = func()
        elapsed = time.perf_counter() - start
        signal.alarm(0)
        return result, elapsed, False
    except TimeoutErr:
        elapsed = time.perf_counter() - start
        return None, elapsed, True
    except RecursionError:
        elapsed = time.perf_counter() - start
        signal.alarm(0)
        return None, elapsed, True
    except Exception:
        elapsed = time.perf_counter() - start
        signal.alarm(0)
        return None, elapsed, False

# Dataset loader

def load_dataset(filepath):
    """Load a dataset file. Each non-comment line: 'VALID/INVALID | formula'."""
    test_set = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' not in line:
                continue
            label, formula_str = line.split('|', 1)
            label = label.strip().upper()
            formula_str = formula_str.strip()
            expected = (label == 'VALID')
            test_set.append((formula_str, expected))
    return test_set

# Benchmark

def benchmark_formula(formula, expected, baseline_depth=6, improved_depth=15, timeout=10):
    """Benchmark one formula on both provers."""

    def run_baseline():
        reset_fresh()
        return prove_baseline(frozenset(), frozenset({formula}), baseline_depth)

    base_result, base_time, base_timeout = run_with_timeout(run_baseline, timeout)

    def run_improved():
        return prove_iterative_deepening(
            frozenset(), frozenset({formula}), improved_depth
        )

    imp_result, imp_time, imp_timeout = run_with_timeout(run_improved, timeout)

    return {
        'expected': expected,
        'baseline_result': base_result,
        'baseline_time': base_time,
        'baseline_timeout': base_timeout,
        'baseline_correct': base_result == expected and not base_timeout,
        'improved_result': imp_result,
        'improved_time': imp_time,
        'improved_timeout': imp_timeout,
        'improved_correct': imp_result == expected and not imp_timeout,
    }


def run_dataset(name, test_set, baseline_depth=6, improved_depth=15, timeout=10, verbose=True):
    """Run benchmark on one dataset, return list of results plus stats."""
    if verbose:
        print(f"\n--- Dataset: {name} ({len(test_set)} formulas) ---")

    results = []
    for i, (formula_str, expected) in enumerate(test_set, 1):
        try:
            formula = parse(formula_str)
        except Exception as e:
            if verbose:
                print(f"  [{i:3d}] PARSE ERROR: {formula_str} ({e})")
            continue

        r = benchmark_formula(formula, expected, baseline_depth, improved_depth, timeout)
        r['dataset'] = name
        r['formula_str'] = formula_str
        results.append(r)

        if verbose:
            b = "OK" if r['baseline_correct'] else ("TO" if r['baseline_timeout'] else "X ")
            i_ = "OK" if r['improved_correct'] else ("TO" if r['improved_timeout'] else "X ")
            display = formula_str if len(formula_str) <= 50 else formula_str[:47] + "..."
            print(f"  [{i:3d}] base={b} ({r['baseline_time']*1000:7.2f}ms)  "
                  f"impr={i_} ({r['improved_time']*1000:7.2f}ms)  | {display}")

    return results


def summarise(name, results):
    """Print a summary of one dataset's results."""
    n = len(results)
    if n == 0:
        return
    base_solved = sum(1 for r in results if r['baseline_correct'])
    imp_solved = sum(1 for r in results if r['improved_correct'])
    base_time = sum(r['baseline_time'] for r in results)
    imp_time = sum(r['improved_time'] for r in results)
    base_to = sum(1 for r in results if r['baseline_timeout'])
    imp_to = sum(1 for r in results if r['improved_timeout'])

    print(f"\n  {name}:")
    print(f"    Total           : {n}")
    print(f"    Baseline solved : {base_solved}/{n} ({100*base_solved/n:.1f}%)")
    print(f"    Improved solved : {imp_solved}/{n} ({100*imp_solved/n:.1f}%)")
    print(f"    Baseline time   : {base_time*1000:.2f} ms")
    print(f"    Improved time   : {imp_time*1000:.2f} ms")
    print(f"    Baseline TOs    : {base_to}")
    print(f"    Improved TOs    : {imp_to}")


def save_results(all_results, output_csv):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'dataset', 'formula', 'expected',
            'baseline_result', 'baseline_correct', 'baseline_time_ms', 'baseline_timeout',
            'improved_result', 'improved_correct', 'improved_time_ms', 'improved_timeout'
        ])
        for r in all_results:
            writer.writerow([
                r['dataset'], r['formula_str'], r['expected'],
                r['baseline_result'], r['baseline_correct'],
                f"{r['baseline_time']*1000:.4f}", r['baseline_timeout'],
                r['improved_result'], r['improved_correct'],
                f"{r['improved_time']*1000:.4f}", r['improved_timeout']
            ])


if __name__ == '__main__':
    DATASETS = [
        ('Textbook',  'datasets/textbook.txt'),
        ('Pelletier', 'datasets/pelletier.txt'),
        ('Generated', 'datasets/generated.txt'),
    ]

    BASELINE_DEPTH = 6
    IMPROVED_DEPTH = 15
    TIMEOUT = 10

    print("=" * 60)
    print("BENCHMARK: Baseline (Algorithm 2) vs Improved Prover")
    print("=" * 60)
    print(f"Baseline depth: {BASELINE_DEPTH}")
    print(f"Improved max depth: {IMPROVED_DEPTH}")
    print(f"Timeout: {TIMEOUT}s")

    all_results = []
    per_dataset = {}

    for name, path in DATASETS:
        if not os.path.exists(path):
            print(f"\n  WARNING: dataset file not found: {path}")
            continue
        test_set = load_dataset(path)
        results = run_dataset(name, test_set, BASELINE_DEPTH, IMPROVED_DEPTH, TIMEOUT)
        all_results.extend(results)
        per_dataset[name] = results

    print("\n" + "=" * 60)
    print("PER-DATASET SUMMARY")
    print("=" * 60)
    for name, results in per_dataset.items():
        summarise(name, results)

    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)
    summarise("ALL DATASETS", all_results)

    save_results(all_results, 'results/results.csv')
    print(f"\n  Results saved to: results/results.csv\n")