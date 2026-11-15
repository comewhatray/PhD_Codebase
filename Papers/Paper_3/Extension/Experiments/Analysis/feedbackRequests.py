import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "Experiment3Results/analysis")
EPOCH = int(sys.argv[2]) if len(sys.argv) > 2 else 99
ITERATIONS = range(6)

# folder -> (label, base representation, is note difference)
EXPERIMENTS = {
    "Kyna": "K&W Note Diff",
    "KynaDefault": "K&W Default",
    "Szeto": "S&W Note Diff",
    "SzetoDefault": "S&W Default",
}
# (note diff folder, default folder, label)
PAIRS = [("Kyna", "KynaDefault", "Karystinaios & Widmer"),
         ("Szeto", "SzetoDefault", "Szeto & Wong")]

# Original label order in the data: classical, modern, baroque, contemporary,
# romantic, impressionist. ERA_ORDER maps display position -> original index.
ERA_NAMES = ["Baroque", "Classical", "Romantic", "Impress.", "Modern", "Contemp."]
ERA_ORDER = [2, 0, 4, 5, 1, 3]
K = 6


def load_run(folder, it):
    """Return (y_true, y_pred, probs) in DISPLAY label order, or None if missing."""
    path = ROOT / folder / f"|Epoch{EPOCH}|Iteration{it}.json"
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    preds = data["TestStage"][0]["Predictions"]
    logits = np.array([p["Probabilities"] for p in preds], dtype=float)
    truth = np.array([int(p["Answer"]) for p in preds])
    # softmax (stable)
    z = logits - logits.max(axis=1, keepdims=True)
    probs = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    # remap original indices into display order
    remap = np.empty(K, dtype=int)
    for display_pos, original in enumerate(ERA_ORDER):
        remap[original] = display_pos
    probs = probs[:, ERA_ORDER]  # columns now in display order
    y_true = remap[truth]
    y_pred = probs.argmax(axis=1)
    return y_true, y_pred, probs


def confusion(y_true, y_pred):
    m = np.zeros((K, K))
    for t, p in zip(y_true, y_pred):
        m[t, p] += 1
    return m


def macro_f1(cm):
    f1s = []
    for c in range(K):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        denom = 2 * tp + fp + fn
        f1s.append(2 * tp / denom if denom else 0.0)
    return float(np.mean(f1s))


def row_norm(cm):
    return 100 * cm / cm.sum(axis=1, keepdims=True)


def latex_matrix(m, decimals=3):
    lines = []
    for i, name in enumerate(ERA_NAMES):
        cells = " & ".join(f"{v:.{decimals}f}" for v in m[i])
        lines.append(f"    \\textbf{{{name}}} & {cells} \\\\\n    \\hline")
    return "\n".join(lines)


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj


# ---------------------------------------------------------------- load
runs = {}
print("=" * 70)
print(f"1. LOADING  (root = {ROOT}, final epoch = {EPOCH})")
print("=" * 70)
for folder in EXPERIMENTS:
    runs[folder] = {}
    for it in ITERATIONS:
        r = load_run(folder, it)
        if r is None:
            print(f"  MISSING: {folder}/|Epoch{EPOCH}|Iteration{it}.json")
        else:
            runs[folder][it] = r
    sizes = sorted({len(r[0]) for r in runs[folder].values()})
    print(f"  {folder:13s} runs found: {sorted(runs[folder])}  test sizes: {sizes}")

# paired label check
for nd, base, label in PAIRS:
    for it in ITERATIONS:
        if it in runs[nd] and it in runs[base]:
            same = np.array_equal(runs[nd][it][0], runs[base][it][0])
            if not same:
                print(f"  WARNING: {label} iteration {it}: test-set order/labels differ "
                      f"between note diff and default. McNemar pairing would be invalid.")

# ---------------------------------------------------------------- metrics
print()
print("=" * 70)
print("2. PER-RUN METRICS (%) and MEAN +/- SD over runs")
print("=" * 70)
summary = {}
for folder, name in EXPERIMENTS.items():
    acc, rec, f1 = [], [], []
    for it in sorted(runs[folder]):
        yt, yp, _ = runs[folder][it]
        cm = confusion(yt, yp)
        acc.append(100 * np.trace(cm) / cm.sum())
        rec.append(100 * np.mean(np.diag(cm) / cm.sum(axis=1)))
        f1.append(100 * macro_f1(cm))
    summary[folder] = (acc, rec, f1)
    print(f"\n  {name} ({folder}), n = {len(acc)} runs")
    print("    run:           " + "  ".join(f"{i:6d}" for i in sorted(runs[folder])))
    print("    accuracy:      " + "  ".join(f"{v:6.2f}" for v in acc))
    print("    mean recall:   " + "  ".join(f"{v:6.2f}" for v in rec))
    print("    macro-F1:      " + "  ".join(f"{v:6.2f}" for v in f1))
    sd = lambda x: np.std(x, ddof=1) if len(x) > 1 else float("nan")
    print(f"    MEAN +/- SD:   accuracy {np.mean(acc):.2f} +/- {sd(acc):.2f} | "
          f"recall {np.mean(rec):.2f} +/- {sd(rec):.2f} | "
          f"macro-F1 {np.mean(f1):.2f} +/- {sd(f1):.2f}")

# ---------------------------------------------------------------- matrices
print()
print("=" * 70)
print("3. AVERAGED CONFUSION MATRICES (rows = true, normalised to 100)")
print("   A = mean of per-run row-normalised matrices")
print("   B = pooled counts, then row-normalised")
print("=" * 70)
for folder, name in EXPERIMENTS.items():
    if not runs[folder]:
        continue
    cms = [confusion(r[0], r[1]) for r in runs[folder].values()]
    A = np.mean([row_norm(c) for c in cms], axis=0)
    B = row_norm(np.sum(cms, axis=0))
    print(f"\n  {name}: diagonal mean A = {np.mean(np.diag(A)):.2f}%  B = {np.mean(np.diag(B)):.2f}%")
    print(f"  LaTeX rows for matrix A ({folder}):")
    print(latex_matrix(A))

# ---------------------------------------------------------------- confidence
print()
print("=" * 70)
print("4. CONFIDENCE RATIO (s_pred - s_correct) / s_correct, softmax scores")
print("   pooled over all errors from all runs; rows = true, cols = predicted")
print("=" * 70)
for folder, name in EXPERIMENTS.items():
    if not runs[folder]:
        continue
    cells = {(t, p): [] for t in range(K) for p in range(K) if t != p}
    for yt, yp, probs in runs[folder].values():
        wrong = np.where(yt != yp)[0]
        for i in wrong:
            s_pred = probs[i, yp[i]]
            s_corr = probs[i, yt[i]]
            cells[(yt[i], yp[i])].append((s_pred - s_corr) / s_corr)
    mean_m = np.zeros((K, K))
    med_m = np.zeros((K, K))
    cnt_m = np.zeros((K, K), dtype=int)
    share_m = np.zeros((K, K))
    for (t, p), vals in cells.items():
        if vals:
            v = np.array(vals)
            mean_m[t, p] = v.mean()
            med_m[t, p] = np.median(v)
            cnt_m[t, p] = len(v)
            share_m[t, p] = 100 * v.max() / v.sum()
    print(f"\n  {name}: MEAN ratio (as in the paper)")
    print(latex_matrix(mean_m))
    print(f"  {name}: MEDIAN ratio")
    print(latex_matrix(med_m))
    print(f"  {name}: errors per cell (count)")
    print(latex_matrix(cnt_m.astype(float), decimals=0))
    biggest = np.unravel_index(np.argmax(mean_m), mean_m.shape)
    print(f"  largest mean cell: {ERA_NAMES[biggest[0]]} -> {ERA_NAMES[biggest[1]]} = "
          f"{mean_m[biggest]:.1f}, from {cnt_m[biggest]} errors; the single largest value "
          f"is {share_m[biggest]:.0f}% of that cell's total")

# ---------------------------------------------------------------- McNemar
print()
print("=" * 70)
print("5. McNEMAR (exact, two-sided), note diff vs default, per run")
print("   a = note diff correct & default wrong ('fixed')")
print("   b = note diff wrong & default correct ('broken')")
print("   Holm correction across the runs of each pair")
print("=" * 70)
for nd, base, label in PAIRS:
    its = [i for i in ITERATIONS if i in runs[nd] and i in runs[base]]
    if not its:
        print(f"\n  {label}: no complete pairs")
        continue
    a_list, b_list, p_list = [], [], []
    print(f"\n  {label}")
    print("    run    a(fixed)  b(broken)   n    acc diff (pp)   p (exact)")
    for it in its:
        yt, p_nd, _ = runs[nd][it]
        _, p_b, _ = runs[base][it]
        c_nd = p_nd == yt
        c_b = p_b == yt
        a = int(np.sum(c_nd & ~c_b))
        b = int(np.sum(~c_nd & c_b))
        n = len(yt)
        p = binomtest(min(a, b), a + b, 0.5).pvalue if a + b > 0 else 1.0
        a_list.append(a);
        b_list.append(b);
        p_list.append(p)
        print(f"    {it:3d}   {a:7d}  {b:9d}  {n:4d}   {100 * (a - b) / n:+9.2f}      {p:.3g}")
    adj = holm(np.array(p_list))
    print("    Holm-adjusted p per run: " + ", ".join(f"{v:.3g}" for v in adj))
    print(f"    runs significant after Holm (alpha 0.05): {int(np.sum(adj < 0.05))} of {len(adj)}")
    A, B = sum(a_list), sum(b_list)
    pooled_p = binomtest(min(A, B), A + B, 0.5).pvalue if A + B else 1.0
    odds = A / B if B else float("inf")
    print(f"    POOLED over runs (not independent, for reference only): "
          f"a = {A}, b = {B}, p = {pooled_p:.3g}, ratio a/b = {odds:.2f}")

print()
print("Done. Paste everything above back into the chat as text.")
