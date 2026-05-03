import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42  # editable text
matplotlib.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 16)
ax.set_ylim(0, 11)
ax.axis('off')

COLOR_INPUT = '#dfe9f3'
COLOR_PROCESS = '#3a7ca5'
COLOR_PROCESS_LIGHT = '#9bc1d9'
COLOR_OUTPUT = '#c8e0c5'
COLOR_BORDER = '#000000'

def draw_box(x, y, w, h, text, fill, fontsize=10, bold=False, text_color='black'):
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.06",
                          facecolor=fill,
                          edgecolor=COLOR_BORDER,
                          linewidth=1.4)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color=text_color)

def draw_arrow(x1, y1, x2, y2):
    arr = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle='-|>', mutation_scale=18,
                          color='#333333', linewidth=1.4)
    ax.add_patch(arr)

# ---------- Title ----------
ax.text(8, 10.5, 'System Architecture',
        ha='center', va='center', fontsize=15, fontweight='bold')

# ---------- Layer 1: Input datasets ----------
ax.text(4.5, 9.85, 'Input: First-Order Logic Formula Files (.txt)',
        ha='center', fontsize=10, style='italic')

draw_box(0.5, 8.5, 2.4, 1.0,
         'Textbook\n(40 formulas)', COLOR_INPUT, fontsize=9)
draw_box(3.3, 8.5, 2.4, 1.0,
         'Pelletier\n(30 formulas)', COLOR_INPUT, fontsize=9)
draw_box(6.1, 8.5, 2.4, 1.0,
         'Generated\n(34 formulas)', COLOR_INPUT, fontsize=9)

# ---------- Layer 2: Parser ----------
draw_box(2.0, 6.5, 5.0, 1.2, '', COLOR_PROCESS_LIGHT)
ax.text(4.5, 7.30, 'Parser  (parser.py)',
        ha='center', va='center', fontsize=10.5, fontweight='bold')
ax.text(4.5, 6.85, 'Tokeniser  ->  Recursive-Descent Parser',
        ha='center', va='center', fontsize=9)

# Arrows from datasets to parser
draw_arrow(1.7, 8.45, 3.0, 7.65)
draw_arrow(4.5, 8.45, 4.5, 7.65)
draw_arrow(7.3, 8.45, 6.0, 7.65)

# AST label
ax.text(4.5, 6.25, 'AST objects',
        ha='center', fontsize=9, style='italic', color='#333')

# ---------- Layer 3: Two provers in parallel ----------
# Baseline prover
draw_box(0.4, 3.2, 4.2, 2.4, '', COLOR_PROCESS_LIGHT)
ax.text(2.5, 5.20, 'Baseline Prover',
        ha='center', fontsize=11, fontweight='bold')
ax.text(2.5, 4.85, '(prover.py)',
        ha='center', fontsize=8.5, style='italic')
ax.text(2.5, 4.40, 'Algorithm 2 from textbook', ha='center', fontsize=9)
ax.text(2.5, 4.05, 'Backward proof search', ha='center', fontsize=9)
ax.text(2.5, 3.70, 'on LK* sequent calculus', ha='center', fontsize=9)
ax.text(2.5, 3.35, 'Fixed depth limit', ha='center', fontsize=9)

# Improved prover
draw_box(5.0, 3.2, 4.2, 2.4, '', COLOR_PROCESS)
ax.text(7.1, 5.20, 'Improved Prover',
        ha='center', fontsize=11, fontweight='bold', color='white')
ax.text(7.1, 4.85, '(improved_prover.py)',
        ha='center', fontsize=8.5, style='italic', color='white')
ax.text(7.1, 4.40, '1. Iterative Deepening', ha='center', fontsize=9, color='white')
ax.text(7.1, 4.05, '2. Loop / Cycle Detection', ha='center', fontsize=9, color='white')
ax.text(7.1, 3.70, '3. Smart Rule Ordering', ha='center', fontsize=9, color='white')
ax.text(7.1, 3.35, '(close > non-branch > branch)', ha='center', fontsize=8, style='italic', color='white')

# Arrows from parser to provers
draw_arrow(3.5, 6.55, 2.5, 5.65)
draw_arrow(5.5, 6.55, 7.1, 5.65)

# ---------- Layer 4: Benchmark runner ----------
draw_box(2.0, 1.2, 5.0, 1.2, '', COLOR_PROCESS_LIGHT)
ax.text(4.5, 2.00, 'Benchmark Runner  (benchmark.py)',
        ha='center', va='center', fontsize=10.5, fontweight='bold')
ax.text(4.5, 1.55, 'Times both provers, records solve / fail / timeout',
        ha='center', va='center', fontsize=9)

# Arrows from provers to benchmark
draw_arrow(2.5, 3.15, 3.5, 2.40)
draw_arrow(7.1, 3.15, 5.5, 2.40)

# ---------- Layer 5: Outputs (right column) ----------
draw_box(10.0, 7.4, 5.0, 1.4,
         'results.csv\n(per-formula results & timings)',
         COLOR_OUTPUT, fontsize=10)

draw_box(10.0, 5.4, 5.0, 1.4,
         'Visualisation (visualise.py)\nVector PDF charts:\nsolve-rate / count comparisons',
         COLOR_OUTPUT, fontsize=10)

draw_box(10.0, 3.4, 5.0, 1.4,
         'Console summary table\n(per-dataset + overall stats)',
         COLOR_OUTPUT, fontsize=10)

# Single arrow from benchmark to outputs region
draw_arrow(7.0, 1.7, 10.0, 4.1)
draw_arrow(7.0, 1.7, 10.0, 6.1)
draw_arrow(7.0, 1.7, 10.0, 8.1)

# ---------- Legend ----------
legend_y = 0.4
draw_box(0.4, legend_y, 0.5, 0.32, '', COLOR_INPUT)
ax.text(1.05, legend_y + 0.16, 'Input datasets', fontsize=9, va='center')

draw_box(3.0, legend_y, 0.5, 0.32, '', COLOR_PROCESS_LIGHT)
ax.text(3.65, legend_y + 0.16, 'Processing module', fontsize=9, va='center')

draw_box(6.0, legend_y, 0.5, 0.32, '', COLOR_PROCESS)
ax.text(6.65, legend_y + 0.16, 'Improved component', fontsize=9, va='center')

draw_box(9.5, legend_y, 0.5, 0.32, '', COLOR_OUTPUT)
ax.text(10.15, legend_y + 0.16, 'Output artefact', fontsize=9, va='center')

plt.savefig('results/architecture_diagram.pdf', format='pdf', bbox_inches='tight')
plt.savefig('results/architecture_diagram.png', format='png',
            bbox_inches='tight', dpi=200)
plt.close()
print("Saved: results/architecture_diagram.pdf")
print("Saved: results/architecture_diagram.png (preview)")