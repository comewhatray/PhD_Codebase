
"""
Regenerate every era table and every era number quoted in the paper.

Reads the final-epoch JSON of every iteration of the four era experiments and
prints, ready to paste:
  1. Loading checks
  2. Table 8   summary (mean per-class recall and macro-F1, mean +/- SD)
  3. Table 9   four averaged confusion matrices
  4. Per-class precision and recall table
  5. Table 11  per-run McNemar (exact, Holm-adjusted)
  6. Table 10  median confidence ratio matrices
  7. Every number quoted in the text (abstract, 6.2, 6.2.1-6.2.4, conclusion)

Usage:
    python3 regenerate_era_results.py [root] [final_epoch]
    python3 regenerate_era_results.py Experiment3Results/analysis 99

The full output is also saved to era_results.txt in the current folder.
Needs numpy and scipy.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "Experiment3Results/analysis")
EPOCH = int(sys.argv[2]) if len(sys.argv) > 2 else 99
ITERATIONS = range(6)

# folder -> (short name, subtable caption name, Table 9 label, Table 10 label)
EXPERIMENTS = {
    "Kyna": ("K&W Note Diff", r"Karystinaios \& Widmer Note Diff.",
             "tab:confusion_era_Kary_diff", "tab:incorrect_era_Kary_diff"),
    "KynaDefault": ("K&W Default", r"Karystinaios \& Widmer Default",
                    "tab:confusion_kyna_default", "tab:incorrect_kyna_default"),
    "Szeto": ("S&W Note Diff", r"Szeto \& Wong Note Diff.",
              "tab:confusion_szeto_diff", "tab:incorrect_szeto_diff"),
    "SzetoDefault": ("S&W Default", r"Szeto \& Wong Default",
                     "tab:confusion_szeto_default", "tab:incorrect_szeto_default"),
}
# (note diff folder, default folder, long name, short LaTeX name)
PAIRS = [("Kyna", "KynaDefault", "Karystinaios & Widmer", r"K\&W"),
         ("Szeto", "SzetoDefault", "Szeto & Wong", r"S\&W")]

# Original label order in the data: classical, modern, baroque, contemporary,
# romantic, impressionist. ERA_ORDER maps display position -> original index.
ERA_NAMES = ["Baroque", "Classical", "Romantic", "Impress.", "Modern", "Contemp."]
ERA_ORDER = [2, 0, 4, 5, 1, 3]
K = 6

_lines = []


def out(text=""):
    print(text)
    _lines.append(text)


def header(title):
    out()
    out("=" * 76)
    out(title)
    out("=" * 76)


# ---------------------------------------------------------------- loading
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
    z = logits - logits.max(axis=1, keepdims=True)
    probs = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    remap = np.empty(K, dtype=int)
    for display_pos, original in enumerate(ERA_ORDER):
        remap[original] = display_pos
    probs = probs[:, ERA_ORDER]
    y_true = remap[truth]
    y_pred = probs.argmax(axis=1)
    return y_true, y_pred, probs


def confusion(y_true, y_pred):
    m = np.zeros((K, K))
    for t, p in zip(y_true, y_pred):
        m[t, p] += 1
    return m


def row_norm(cm):
    return 100 * cm / cm.sum(axis=1, keepdims=True)


def prf(cm):
    tp = np.diag(cm)
    pred_tot = cm.sum(axis=0)
    true_tot = cm.sum(axis=1)
    prec = np.divide(tp, pred_tot, out=np.zeros(K), where=pred_tot > 0)
    rec = np.divide(tp, true_tot, out=np.zeros(K), where=true_tot > 0)
    den = prec + rec
    f1 = np.divide(2 * prec * rec, den, out=np.zeros(K), where=den > 0)
    return 100 * prec, 100 * rec, 100 * f1


def sd(x, axis=None):
    x = np.asarray(x, dtype=float)
    n = x.shape[0] if axis == 0 else x.size
    return np.std(x, axis=axis, ddof=1) if n > 1 else np.nan


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj


def latex_p(p):
    if p >= 0.001:
        return f"{p:.3f}"
    mant, exp = f"{p:.1e}".split("e")
    return f"${mant} \\times 10^{{{int(exp)}}}$"


def rng(values, decimals=1):
    v = np.asarray(values, dtype=float)
    return f"{v.min():.{decimals}f} to {v.max():.{decimals}f}"


header(f"1. LOADING (root = {ROOT}, final epoch = {EPOCH})")
runs = {}
problems = False
for folder in EXPERIMENTS:
    runs[folder] = {}
    for it in ITERATIONS:
        r = load_run(folder, it)
        if r is None:
            out(f"  MISSING: {folder}/|Epoch{EPOCH}|Iteration{it}.json")
            problems = True
        else:
            runs[folder][it] = r
    sizes = sorted({len(r[0]) for r in runs[folder].values()})
    out(f"  {folder:13s} runs found: {sorted(runs[folder])}  test sizes: {sizes}")
for nd, base, label, _ in PAIRS:
    for it in ITERATIONS:
        if it in runs[nd] and it in runs[base]:
            if not np.array_equal(runs[nd][it][0], runs[base][it][0]):
                out(f"  WARNING: {label} iteration {it}: test labels differ between "
                    f"note diff and default, so the McNemar pairing is invalid.")
                problems = True
# same test set across all four experiments for a given iteration?
for it in ITERATIONS:
    labels = [runs[f][it][0] for f in EXPERIMENTS if it in runs[f]]
    if len(labels) > 1 and not all(np.array_equal(labels[0], x) for x in labels[1:]):
        out(f"  NOTE: iteration {it}: K&W and S&W test labels are not in the same order "
            f"(only matters for the untested S&W vs K&W comparison).")
if not problems:
    out("  All 24 runs found and all note diff / default pairs share the same test labels.")
if any(len(runs[f]) == 0 for f in EXPERIMENTS):
    out("  At least one experiment has no runs. Stopping.")
    Path("era_results.txt").write_text("\n".join(_lines) + "\n")
    sys.exit(1)

# ---------------------------------------------------------------- per-run stats
stats = {}
for folder in EXPERIMENTS:
    acc, rec, f1, P, R, F, cms = [], [], [], [], [], [], []
    for it in sorted(runs[folder]):
        yt, yp, _ = runs[folder][it]
        cm = confusion(yt, yp)
        p, r, f = prf(cm)
        cms.append(cm)
        acc.append(100 * np.trace(cm) / cm.sum())
        rec.append(r.mean()); f1.append(f.mean())
        P.append(p); R.append(r); F.append(f)
    A = np.mean([row_norm(c) for c in cms], axis=0)
    stats[folder] = dict(acc=np.array(acc), rec=np.array(rec), f1=np.array(f1),
                         P=np.array(P), R=np.array(R), F=np.array(F), cms=cms, A=A,
                         its=sorted(runs[folder]))

# ---------------------------------------------------------------- Table 8
header("2. TABLE 8: summary (paste over the tabular)")
out(r"\begin{tabular}{|l|c|c|c|c|}")
out(r"\hline")
out(r"& \multicolumn{2}{c|}{\textbf{Mean per-class recall}} & \multicolumn{2}{c|}{\textbf{Macro-F1}} \\")
out(r"\hline")
out(r"\textbf{Method} & \textbf{Original} & \textbf{Note Diff.} & \textbf{Original} & \textbf{Note Diff.} \\")
out(r"\hline")
for nd, base, label, _ in PAIRS:
    def cell(folder, key):
        s = stats[folder][key]
        return f"{s.mean():.1f} $\\pm$ {sd(s):.1f}"
    out(f"{label.replace('&', chr(92) + '&')} & {cell(base, 'rec')} & {cell(nd, 'rec')} & "
        f"{cell(base, 'f1')} & {cell(nd, 'f1')} \\\\")
    out(r"\hline")
out(r"\end{tabular}")
out()
out("  Two-decimal values (accuracy | mean recall | macro-F1), mean +/- SD:")
for folder, (name, *_rest) in EXPERIMENTS.items():
    s = stats[folder]
    out(f"    {name:14s} {s['acc'].mean():.2f} +/- {sd(s['acc']):.2f} | "
        f"{s['rec'].mean():.2f} +/- {sd(s['rec']):.2f} | {s['f1'].mean():.2f} +/- {sd(s['f1']):.2f}")

# ---------------------------------------------------------------- Table 9
header("3. TABLE 9: confusion matrices (paste over the whole table)")
out(r"\begin{table*}[t]")
out(r"\centering")
out(r"\caption{Confusion Matrices - Era Classification Comparison (mean over six runs; rows are true eras and sum to 100\%)}")
out(r"\label{tab:combined_era_confusion}")
out()
TAB_HEAD = (r"    \textbf{True/Pred} & \textbf{Baroque} & \textbf{Classical} & \textbf{Romantic} & "
            r"\textbf{Impress.} & \textbf{Modern} & \textbf{Contemp.} \\")


def subtable(caption, label, rows):
    out(r"\begin{subtable}{\textwidth}")
    out(r"    \centering")
    out(f"    \\caption{{{caption}}}")
    out(f"    \\label{{{label}}}")
    out(r"    \resizebox{\textwidth}{!}{%")
    out(r"    \begin{tabular}{|l|c|c|c|c|c|c|}")
    out(r"    \hline")
    out(TAB_HEAD)
    out(r"    \hline")
    for name, cells in zip(ERA_NAMES, rows):
        out(f"    \\textbf{{{name}}} & " + " & ".join(cells) + r" \\")
        out(r"    \hline")
    out(r"    \end{tabular}%")
    out(r"    }")
    out(r"\end{subtable}")


for idx, (folder, (name, cap, lab9, lab10)) in enumerate(EXPERIMENTS.items()):
    A = stats[folder]["A"]
    rows = [[f"{v:.3f}" for v in A[i]] for i in range(K)]
    subtable(f"{cap} (Mean per-class recall: {np.mean(np.diag(A)):.2f}\\%)", lab9, rows)
    out(r"\hspace{\parindent}" if idx % 2 == 0 else "")
    if idx == 1:
        out(r"\vspace{1em}")
        out()
out(r"\end{table*}")

# ---------------------------------------------------------------- per-class table
header("4. PER-CLASS PRECISION AND RECALL TABLE (paste over the whole table)")
out(r"\begin{table*}[t]")
out(r"\centering")
out(r"\caption{Era classification: per-class precision (P) and recall (R), mean over six runs (\%)}")
out(r"\label{tab:era_per_class}")
out(r"\resizebox{\textwidth}{!}{%")
out(r"\begin{tabular}{|l|c|c|c|c|c|c|c|c|}")
out(r"\hline")
out(r" & \multicolumn{2}{c|}{\textbf{K\&W Note Diff.}} & \multicolumn{2}{c|}{\textbf{K\&W Default}} & "
    r"\multicolumn{2}{c|}{\textbf{S\&W Note Diff.}} & \multicolumn{2}{c|}{\textbf{S\&W Default}} \\")
out(r"\hline")
out(r"\textbf{Era} & \textbf{P} & \textbf{R} & \textbf{P} & \textbf{R} & \textbf{P} & \textbf{R} & \textbf{P} & \textbf{R} \\")
out(r"\hline")
for c in range(K):
    cells = []
    for folder in EXPERIMENTS:
        cells.append(f"{stats[folder]['P'].mean(0)[c]:.1f} & {stats[folder]['R'].mean(0)[c]:.1f}")
    out(f"\\textbf{{{ERA_NAMES[c]}}} & " + " & ".join(cells) + r" \\")
    out(r"\hline")
cells = [f"{stats[f]['P'].mean():.1f} & {stats[f]['R'].mean():.1f}" for f in EXPERIMENTS]
out(r"\textbf{Mean} & " + " & ".join(cells) + r" \\")
out(r"\hline")
out(r"\end{tabular}%")
out(r"}")
out(r"\end{table*}")

# ---------------------------------------------------------------- McNemar
mc = {}
for nd, base, label, short in PAIRS:
    rows, pvals = [], []
    for it in ITERATIONS:
        if it not in runs[nd] or it not in runs[base]:
            continue
        yt, p_nd, _ = runs[nd][it]
        _, p_b, _ = runs[base][it]
        c_nd, c_b = p_nd == yt, p_b == yt
        both = int(np.sum(c_nd & c_b)); a = int(np.sum(c_nd & ~c_b))
        b = int(np.sum(~c_nd & c_b)); neither = int(np.sum(~c_nd & ~c_b))
        p = binomtest(min(a, b), a + b, 0.5).pvalue if a + b > 0 else 1.0
        rows.append(dict(it=it, both=both, a=a, b=b, neither=neither, n=len(yt),
                         diff=100 * (a - b) / len(yt)))
        pvals.append(p)
    adj = holm(np.array(pvals)) if pvals else np.array([])
    for r, p, q in zip(rows, pvals, adj):
        r["p"], r["adj"] = p, q
    mc[nd] = rows

n_test = sorted({r["n"] for rows in mc.values() for r in rows})
n_text = f"{n_test[0]:,}".replace(",", "{,}") if len(n_test) == 1 else "varies"
header("5. TABLE 11: per-run McNemar (paste over the whole table)")
out(r"\begin{table*}[t]")
out(r"\centering")
out(r"\caption{Era classification: McNemar comparison of each base representation with its note difference "
    f"graph, per run ($n = {n_text}$ test pieces). "
    r"Fixed ($a$): correct under the note difference model only; broken ($b$): correct under the original "
    r"model only. Adjusted $p$: exact two-sided test, Holm-corrected over the six runs of each pair.}")
out(r"\label{tab:era_mcnemar}")
out(r"\renewcommand{\arraystretch}{1.25}")
out(r"\resizebox{\textwidth}{!}{%")
out(r"\begin{tabular}{|l|c|c|c|c|c|c|c|}")
out(r"\hline")
out(r"\textbf{Pair} & \textbf{Run} & \textbf{Both correct} & \textbf{Fixed ($a$)} & \textbf{Broken ($b$)} & "
    r"\textbf{Both wrong} & \textbf{$a/b$} & \textbf{Adj.\ $p$} \\")
out(r"\hline")
for nd, base, label, short in PAIRS:
    for r in mc[nd]:
        ratio = f"{r['a'] / r['b']:.2f}" if r["b"] else "--"
        out(f"{short} & {r['it'] + 1} & {r['both']} & {r['a']} & {r['b']} & {r['neither']} & "
            f"{ratio} & {latex_p(r['adj'])} \\\\")
        out(r"\hline")
out(r"\end{tabular}%")
out(r"}")
out(r"\end{table*}")

# ---------------------------------------------------------------- confidence
conf = {}
for folder in EXPERIMENTS:
    cells = {(t, p): [] for t in range(K) for p in range(K) if t != p}
    for yt, yp, probs in runs[folder].values():
        for i in np.where(yt != yp)[0]:
            s_pred, s_corr = probs[i, yp[i]], probs[i, yt[i]]
            cells[(yt[i], yp[i])].append((s_pred - s_corr) / s_corr)
    mean_m = np.full((K, K), np.nan); med_m = np.full((K, K), np.nan)
    cnt_m = np.zeros((K, K), dtype=int); share_m = np.full((K, K), np.nan)
    for (t, p), vals in cells.items():
        if vals:
            v = np.array(vals)
            mean_m[t, p] = v.mean(); med_m[t, p] = np.median(v)
            cnt_m[t, p] = len(v); share_m[t, p] = 100 * v.max() / v.sum()
    conf[folder] = dict(mean=mean_m, med=med_m, cnt=cnt_m, share=share_m)

header("6. TABLE 10: median confidence ratio (paste over the whole table)")
out(r"\begin{table*}[t]")
out(r"\centering")
out(r"\caption{Median Confidence Ratio of Incorrect Predictions - Era Classification Comparison}")
out(r"\label{tab:combined_incorrect_matrices}")
out()
for idx, (folder, (name, cap, lab9, lab10)) in enumerate(EXPERIMENTS.items()):
    med = conf[folder]["med"]
    rows = [["--" if (i == j or np.isnan(med[i, j])) else f"{med[i, j]:.3f}" for j in range(K)]
            for i in range(K)]
    subtable(cap, lab10, rows)
    out(r"\hspace{\parindent}" if idx % 2 == 0 else "")
    if idx == 1:
        out(r"\vspace{1em}")
        out()
out(r"\end{table*}")

# ---------------------------------------------------------------- numbers in the text
header("7. NUMBERS QUOTED IN THE TEXT")
short = {f: EXPERIMENTS[f][0] for f in EXPERIMENTS}
FOLDERS = list(EXPERIMENTS)

out("\n-- Abstract, Section 6.2 opening, Conclusion --")
for nd, base, label, _ in PAIRS:
    r0, r1 = stats[base]["rec"].mean(), stats[nd]["rec"].mean()
    out(f"  {label}: mean per-class recall {r0:.1f}% -> {r1:.1f}%  (gain {r1 - r0:.1f} points; "
        f"rounded {r0:.0f}% -> {r1:.0f}%)")
    diffs = [r["diff"] for r in mc[nd]]
    wins = sum(d > 0 for d in diffs)
    out(f"    per-run accuracy gain: {rng(diffs)} points; note diff ahead in {wins} of {len(diffs)} runs")
best = max(FOLDERS, key=lambda f: stats[f]["rec"].mean())
out(f"  Best era model: {short[best]} at {stats[best]['rec'].mean():.1f}% mean per-class recall")
common = [i for i in stats["Szeto"]["its"] if i in stats["Kyna"]["its"]]
d_rec = [stats["Szeto"]["rec"][stats["Szeto"]["its"].index(i)]
         - stats["Kyna"]["rec"][stats["Kyna"]["its"].index(i)] for i in common]
d_acc = [stats["Szeto"]["acc"][stats["Szeto"]["its"].index(i)]
         - stats["Kyna"]["acc"][stats["Kyna"]["its"].index(i)] for i in common]
out(f"  S&W Note Diff minus K&W Note Diff, per run: recall {rng(d_rec)} points, "
    f"accuracy {rng(d_acc)} points (S&W ahead in {sum(d > 0 for d in d_acc)} of {len(d_acc)} runs)")
out("  Chance baseline for six eras: 16.7%")

out("\n-- Section 6.2, second paragraph: most frequent prediction per true era --")
for folder in FOLDERS:
    A = stats[folder]["A"]
    notes = []
    for i in range(K):
        j = int(np.argmax(A[i]))
        if j != i:
            notes.append(f"{ERA_NAMES[i]} -> {ERA_NAMES[j]} ({A[i, j]:.1f} vs own {A[i, i]:.1f})")
    out(f"  {short[folder]:14s} " + ("correct era is the most frequent prediction for every era"
                                     if not notes else "exceptions: " + "; ".join(notes)))

out("\n-- Section 6.2.1: per-era recall and its change (note diff minus default, points) --")
out("  " + " " * 12 + "".join(f"{short[f]:>16s}" for f in FOLDERS))
for c in range(K):
    out(f"  {ERA_NAMES[c]:12s}" + "".join(f"{stats[f]['A'][c, c]:16.1f}" for f in FOLDERS))
for nd, base, label, _ in PAIRS:
    d = np.diag(stats[nd]["A"]) - np.diag(stats[base]["A"])
    out(f"  {label} change: " + ", ".join(f"{ERA_NAMES[c]} {d[c]:+.1f}" for c in range(K)))

out("\n-- Section 6.2.3: lowest-recall eras per model --")
for folder in FOLDERS:
    diag = np.diag(stats[folder]["A"])
    order = np.argsort(diag)
    out(f"  {short[folder]:14s} lowest: {ERA_NAMES[order[0]]} ({diag[order[0]]:.1f}%), "
        f"second: {ERA_NAMES[order[1]]} ({diag[order[1]]:.1f}%), third: {ERA_NAMES[order[2]]} ({diag[order[2]]:.1f}%)")
out(f"  Classical recall range across models: "
    f"{rng([stats[f]['A'][1, 1] for f in FOLDERS])}%")

out("\n-- Section 6.2.1: per-class precision --")
for nd, base, label, _ in PAIRS:
    dp = stats[nd]["P"].mean(0) - stats[base]["P"].mean(0)
    out(f"  {label} precision change: " + ", ".join(f"{ERA_NAMES[c]} {dp[c]:+.1f}" for c in range(K)))
for c, nm in [(2, "Romantic"), (1, "Classical")]:
    out(f"  {nm}: precision {rng([stats[f]['P'].mean(0)[c] for f in FOLDERS], 0)}%, "
        f"recall {rng([stats[f]['R'].mean(0)[c] for f in FOLDERS], 0)}% across the four models")
    out("    per model (P / R): " + "; ".join(
        f"{short[f]} {stats[f]['P'].mean(0)[c]:.1f} / {stats[f]['R'].mean(0)[c]:.1f}" for f in FOLDERS))
sd_r = [sd(stats[f]["R"], axis=0)[c] for f in FOLDERS for c in (4, 5)]
sd_p = [sd(stats[f]["P"], axis=0)[c] for f in FOLDERS for c in (4, 5)]
out(f"  Modern and Contemporary across runs: recall SD {rng(sd_r, 0)} points, precision SD {rng(sd_p, 0)} points")

out("\n-- Section 6.2.2: McNemar --")
all_adj = []
for nd, base, label, _ in PAIRS:
    rows = mc[nd]
    a = [r["a"] for r in rows]; b = [r["b"] for r in rows]
    ratios = [r["a"] / r["b"] for r in rows if r["b"]]
    adj = [r["adj"] for r in rows]; all_adj += adj
    out(f"  {label}: corrected {min(a)} to {max(a)}, broke {min(b)} to {max(b)}, "
        f"ratio a/b {rng(ratios, 2)}")
    out(f"    summed over runs: corrected {sum(a):,}, broke {sum(b):,}; "
        f"runs significant after Holm (0.05): {sum(q < 0.05 for q in adj)} of {len(adj)}; "
        f"largest adjusted p = {max(adj):.2g}")
out(f"  Largest adjusted p over all {len(all_adj)} tests: {max(all_adj):.2g}")

out("\n-- Section 6.2.4: confidence analysis --")
adj_mask = np.array([[abs(i - j) == 1 for j in range(K)] for i in range(K)])
off_mask = ~np.eye(K, dtype=bool)
big, shares, adj_share, rom, mod, mins = [], [], [], [], [], []
for folder in FOLDERS:
    c = conf[folder]
    pos = np.unravel_index(np.nanargmax(c["mean"]), c["mean"].shape)
    big.append(c["mean"][pos]); shares.append(c["share"][pos])
    tot = c["cnt"].sum()
    adj_share.append(100 * c["cnt"][adj_mask].sum() / tot)
    rom.append(100 * c["cnt"][:, 2].sum() / tot); mod.append(100 * c["cnt"][:, 4].sum() / tot)
    mins.append(c["cnt"][off_mask].min())
    out(f"  {short[folder]:14s} largest mean cell {ERA_NAMES[pos[0]]} -> {ERA_NAMES[pos[1]]} = "
        f"{c['mean'][pos]:.3g} ({c['cnt'][pos]} errors, largest value = {c['share'][pos]:.0f}% of cell total); "
        f"neighbouring-era share {adj_share[-1]:.1f}%; predicted Romantic {rom[-1]:.1f}%, Modern {mod[-1]:.1f}%")
out(f"  Largest cell mean per model ranges from {min(big):.2g} to {max(big):.2g}; "
    f"single-prediction share at least {min(shares):.0f}%")
out(f"  Neighbouring-era errors: {rng(adj_share, 0)}% of all errors (10 of 30 cells; 33% if even)")
out(f"  Errors predicted as Romantic: {rng(rom, 0)}%; as Modern: {rng(mod, 0)}%")
out(f"  Smallest cell count: {min(mins)}")


def cell_range(t, p, key, dec):
    return rng([conf[f][key][t, p] for f in FOLDERS], dec)


for t, p in [(5, 4), (1, 2), (4, 5)]:
    out(f"  {ERA_NAMES[t]} predicted as {ERA_NAMES[p]}: {cell_range(t, p, 'cnt', 0)} errors across models")
for t, p in [(4, 5), (5, 4), (2, 1), (1, 2), (0, 3), (3, 0)]:
    out(f"  Median ratio, {ERA_NAMES[t]} predicted as {ERA_NAMES[p]}: {cell_range(t, p, 'med', 2)}")
im = [conf[f]["med"][3, 4] for f in FOLDERS] + [conf[f]["med"][4, 3] for f in FOLDERS]
out(f"  Median ratio, Impressionist and Modern (both directions): {rng(im, 1)}")
a_means = [np.nanmean(conf[f]["med"][adj_mask]) for f in FOLDERS]
n_means = [np.nanmean(conf[f]["med"][off_mask & ~adj_mask]) for f in FOLDERS]
out(f"  Mean of cell medians: neighbouring {rng(a_means, 2)}, non-neighbouring {rng(n_means, 2)}")
for f, a_, n_ in zip(FOLDERS, a_means, n_means):
    out(f"    {short[f]:14s} neighbouring {a_:.2f}, non-neighbouring {n_:.2f}")

out()
out("Done. The full output is saved in era_results.txt. Send that file, or paste everything above.")
Path("era_results.txt").write_text("\n".join(_lines) + "\n")