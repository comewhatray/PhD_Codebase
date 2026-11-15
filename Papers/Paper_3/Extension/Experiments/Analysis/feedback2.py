#!/usr/bin/env python3
"""
Per-class precision, recall and F1 for the four era experiments.
Reads the final-epoch JSON of every iteration (same files as analyse_era.py)
and prints mean +/- SD over the runs, plus LaTeX table rows.

Usage:
    python3 per_class_era.py [root] [final_epoch]
    python3 per_class_era.py Experiment3Results/analysis 99

Needs only numpy.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "Experiment3Results/analysis")
EPOCH = int(sys.argv[2]) if len(sys.argv) > 2 else 99
ITERATIONS = range(6)

EXPERIMENTS = {
    "Kyna": "K&W Note Diff",
    "KynaDefault": "K&W Default",
    "Szeto": "S&W Note Diff",
    "SzetoDefault": "S&W Default",
}

# Original label order in the data: classical, modern, baroque, contemporary,
# romantic, impressionist. ERA_ORDER maps display position -> original index.
ERA_NAMES = ["Baroque", "Classical", "Romantic", "Impress.", "Modern", "Contemp."]
ERA_ORDER = [2, 0, 4, 5, 1, 3]
K = 6


def load_run(folder, it):
    path = ROOT / folder / f"|Epoch{EPOCH}|Iteration{it}.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    preds = data["TestStage"][0]["Predictions"]
    logits = np.array([p["Probabilities"] for p in preds], dtype=float)
    truth = np.array([int(p["Answer"]) for p in preds])
    remap = np.empty(K, dtype=int)
    for display_pos, original in enumerate(ERA_ORDER):
        remap[original] = display_pos
    y_true = remap[truth]
    y_pred = logits[:, ERA_ORDER].argmax(axis=1)   # argmax of logits = argmax of softmax
    return y_true, y_pred


def per_class(y_true, y_pred):
    cm = np.zeros((K, K))
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    tp = np.diag(cm)
    pred_tot = cm.sum(axis=0)
    true_tot = cm.sum(axis=1)
    prec = np.divide(tp, pred_tot, out=np.zeros(K), where=pred_tot > 0)
    rec = np.divide(tp, true_tot, out=np.zeros(K), where=true_tot > 0)
    denom = prec + rec
    f1 = np.divide(2 * prec * rec, denom, out=np.zeros(K), where=denom > 0)
    return 100 * prec, 100 * rec, 100 * f1


def sd(x):
    return np.std(x, axis=0, ddof=1) if len(x) > 1 else np.full(K, np.nan)


results = {}
for folder, name in EXPERIMENTS.items():
    P, R, F = [], [], []
    found = []
    for it in ITERATIONS:
        run = load_run(folder, it)
        if run is None:
            print(f"MISSING: {folder}/|Epoch{EPOCH}|Iteration{it}.json")
            continue
        found.append(it)
        p, r, f = per_class(*run)
        P.append(p); R.append(r); F.append(f)
    if not P:
        continue
    P, R, F = np.array(P), np.array(R), np.array(F)
    results[folder] = (P.mean(0), sd(P), R.mean(0), sd(R), F.mean(0), sd(F))
    print("=" * 72)
    print(f"{name} ({folder}), runs found: {found}")
    print("=" * 72)
    print(f"  {'Era':10s} {'Precision':>16s} {'Recall':>16s} {'F1':>16s}")
    for c in range(K):
        print(f"  {ERA_NAMES[c]:10s} "
              f"{P.mean(0)[c]:7.1f} +/- {sd(P)[c]:4.1f} "
              f"{R.mean(0)[c]:7.1f} +/- {sd(R)[c]:4.1f} "
              f"{F.mean(0)[c]:7.1f} +/- {sd(F)[c]:4.1f}")
    print(f"  {'Macro':10s} {P.mean():7.1f}          {R.mean():7.1f}          {F.mean():7.1f}")
    print()

# LaTeX rows: one row per era, precision and recall for each of the four models
print("=" * 72)
print("LaTeX rows (precision / recall, mean over runs, %), columns in the order:")
print("  " + " | ".join(EXPERIMENTS[f] for f in EXPERIMENTS if f in results))
print("=" * 72)
for c in range(K):
    cells = []
    for folder in EXPERIMENTS:
        if folder in results:
            pm, _, rm, _, _, _ = results[folder]
            cells.append(f"{pm[c]:.1f} & {rm[c]:.1f}")
    print(f"\\textbf{{{ERA_NAMES[c]}}} & " + " & ".join(cells) + " \\\\")
    print("\\hline")

print()
print("Done. Paste everything above back into the chat as text.")