# scripts/plot_results.py
import json
import matplotlib.pyplot as plt
import ast
import numpy as np

# Load JSON results
with open("FileHits/file_hit_with_summary.json") as f:
    with_summary = json.load(f)
with open("FileHits/file_hits_no_summary.json") as f:
    without_summary = json.load(f)

x = sorted(int(k) for k in with_summary.keys())
y_with = [with_summary[str(i)] / 300 * 100 for i in x]
y_without = [without_summary[str(i)] / 300 * 100 for i in x]

plt.figure(figsize=(10, 6))
plt.plot(x, y_with, marker='o', label="With Summary", linewidth=2)
plt.plot(x, y_without, marker='s', label="Without Summary", linewidth=2)
for x_i, y_w, y_wo in zip(x, y_with, y_without):
    dx = -0.15 if x_i == 1 else 0
    plt.text(x_i + dx, y_w + 1, f"{y_w:.1f}%", ha='center', fontsize=8)
    plt.text(x_i + dx, y_wo - 3, f"{y_wo:.1f}%", ha='center', fontsize=8)
plt.xlabel("Top-N Files", fontsize=12)
plt.ylabel("File Hit Percentage", fontsize=12)
plt.title("File Hit % With vs Without Summary", fontsize=14)
plt.tick_params(axis='x', pad=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(x)
plt.gca().invert_xaxis()
plt.tight_layout()
plt.show()

# Additional plotting for parameter tuning results (if needed)
with open("results-Copy1.json", "r") as f:
    raw_data = json.load(f)
    list_of_file_hit_values = {ast.literal_eval(k): v for k, v in raw_data.items()}

best_combo = max(list_of_file_hit_values, key=list_of_file_hit_values.get)
best_n, best_w_base, best_w_semantic = best_combo
best_score = list_of_file_hit_values[best_combo]
print(f"Best N: {best_n}, Best BM25 weight: {best_w_base}, Semantic weight: {best_w_semantic}")
print(f"Best Score: {best_score} ({(best_score/300)*100:.2f}%)")

plt.figure(figsize=(10, 5))
x_labels = []
x_positions = []
n_values = sorted(set(n for (n, _, _) in list_of_file_hit_values.keys()))
for n in n_values:
    data_points = [
        (w_base, w_semantic, list_of_file_hit_values[(n, w_base, w_semantic)] / 300 * 100)
        for (n_val, w_base, w_semantic) in list_of_file_hit_values.keys() if n_val == n
    ]
    x_vals, y_vals, percentages = zip(*data_points)
    plt.scatter(x_vals, percentages, label=f'n={n}', marker='o')
    plt.plot(x_vals, percentages, linestyle='-', alpha=0.7)
    for x_val, pct in zip(x_vals, percentages):
        plt.text(x_val, pct + 1.2, f"{pct:.1f}%", fontsize=8, ha='center')
    if not x_labels:
        x_labels = [f"{w_base:.1f},{w_semantic:.1f}" for w_base, w_semantic in zip(x_vals, y_vals)]
        x_positions = list(x_vals)
plt.xticks(x_positions, x_labels, rotation=0)
plt.xlabel("BM25 Weight, Semantic Weight")
plt.ylabel("File Hit Percentage")
plt.title("File Hit Percentage for Different n Values")
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()
