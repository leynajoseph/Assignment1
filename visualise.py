import csv
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42  


def load_results(csv_path='results/results.csv'):
    """Load benchmark results from CSV."""
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results


def aggregate_by_dataset(results):
    """Group results by dataset and compute totals."""
    datasets = {}
    for r in results:
        ds = r['dataset']
        if ds not in datasets:
            datasets[ds] = {'total': 0, 'base_solved': 0, 'imp_solved': 0,
                            'base_time': 0.0, 'imp_time': 0.0}
        datasets[ds]['total'] += 1
        if r['baseline_correct'] == 'True':
            datasets[ds]['base_solved'] += 1
        if r['improved_correct'] == 'True':
            datasets[ds]['imp_solved'] += 1
        datasets[ds]['base_time'] += float(r['baseline_time_ms'])
        datasets[ds]['imp_time'] += float(r['improved_time_ms'])
    return datasets


def plot_solved_counts(datasets, output_path='results/chart_solved_counts.pdf'):
    """Bar chart comparing solved counts per dataset."""
    names = list(datasets.keys())
    base_solved = [datasets[n]['base_solved'] for n in names]
    imp_solved = [datasets[n]['imp_solved'] for n in names]
    totals = [datasets[n]['total'] for n in names]

    x = range(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars1 = ax.bar([i - width/2 for i in x], base_solved, width,
                    label='Baseline (Algorithm 2)', color='#888888', edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], imp_solved, width,
                    label='Improved Prover', color='#3a7ca5', edgecolor='black')

    # Annotate counts on top of bars
    for bar, val, total in zip(bars1, base_solved, totals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.4,
                f"{val}/{total}", ha='center', fontsize=9)
    for bar, val, total in zip(bars2, imp_solved, totals):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.4,
                f"{val}/{total}", ha='center', fontsize=9)

    ax.set_xlabel('Dataset', fontsize=11)
    ax.set_ylabel('Formulas solved', fontsize=11)
    ax.set_title('Solved Formulas per Dataset', fontsize=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_ylim(0, max(totals) * 1.15)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def plot_solve_percentage(datasets, output_path='results/chart_solve_percent.pdf'):
    """Bar chart showing solve percentage per dataset."""
    names = list(datasets.keys())
    base_pct = [100 * datasets[n]['base_solved'] / datasets[n]['total'] for n in names]
    imp_pct = [100 * datasets[n]['imp_solved'] / datasets[n]['total'] for n in names]

    x = range(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars1 = ax.bar([i - width/2 for i in x], base_pct, width,
                   label='Baseline (Algorithm 2)', color='#888888', edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], imp_pct, width,
                   label='Improved Prover', color='#3a7ca5', edgecolor='black')

    for bar, val in zip(bars1, base_pct):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.0,
                f"{val:.1f}%", ha='center', fontsize=9)
    for bar, val in zip(bars2, imp_pct):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.0,
                f"{val:.1f}%", ha='center', fontsize=9)

    ax.set_xlabel('Dataset', fontsize=11)
    ax.set_ylabel('Solve rate (%)', fontsize=11)
    ax.set_title('Solve Rate per Dataset', fontsize=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_ylim(0, 110)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


def plot_overall_summary(datasets, output_path='results/chart_overall.pdf'):
    """Single bar chart showing overall solved count across all datasets."""
    total_n = sum(d['total'] for d in datasets.values())
    base_total = sum(d['base_solved'] for d in datasets.values())
    imp_total = sum(d['imp_solved'] for d in datasets.values())

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(['Baseline\n(Algorithm 2)', 'Improved\nProver'],
                  [base_total, imp_total],
                  color=['#888888', '#3a7ca5'], edgecolor='black', width=0.55)

    for bar, val in zip(bars, [base_total, imp_total]):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.8,
                f"{val}/{total_n}\n({100*val/total_n:.1f}%)",
                ha='center', fontsize=10)

    ax.set_ylabel('Total formulas solved', fontsize=11)
    ax.set_title(f'Overall Performance (across {total_n} formulas)', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_ylim(0, total_n * 1.12)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")


if __name__ == '__main__':
    print("Generating result charts...")
    results = load_results('results/results.csv')
    datasets = aggregate_by_dataset(results)

    plot_solved_counts(datasets)
    plot_solve_percentage(datasets)
    plot_overall_summary(datasets)

    print("\nDone! Charts are vector PDFs ready for the LNCS report.")