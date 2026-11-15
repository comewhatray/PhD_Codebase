import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 7)
ax.axis("off")
ax.set_title("Graph Neural Network Architecture", fontsize=18, fontweight="bold")

BLUE, GREEN, YELLOW, RED = "#ADD8E6", "#90EE90", "#FFFFE0", "#F08080"
W, H, Y = 2.0, 1.4, 3.0
boxes = [
    (0.6,  "GraphSAGE\nConvolutional\n(Input)",    BLUE,
     "Input: 3 features\n(pitch diff, onset diff,\ntemporal gap)\nReLU activation\nDropout: 0.2"),
    (3.4,  "GraphSAGE\nConvolutional\n(Hidden 1)", GREEN,
     "Hidden: 75 dimensions\nReLU activation\nDropout: 0.2"),
    (6.2,  "GraphSAGE\nConvolutional\n(Hidden 2)", GREEN,
     "Hidden: 75 dimensions\nReLU activation\nNo dropout"),
    (9.0,  "Global Mean\nPooling",                YELLOW,
     "Aggregates node-level\nrepresentations to\ngraph-level\nDropout: 0.2"),
    (11.8, "Linear\nOutput",                      RED,
     "One score per class\n(5 composers or 6 eras)\nRaw logits; softmax\napplied afterwards"),
]

for x, label, colour, note in boxes:
    ax.add_patch(FancyBboxPatch((x, Y), W, H, boxstyle="round,pad=0.05",
                                facecolor=colour, edgecolor="black", linewidth=2.5))
    ax.text(x + W / 2, Y + H / 2, label, ha="center", va="center",
            fontsize=12, fontweight="bold")
    ax.text(x + W / 2, Y - 0.25, note, ha="center", va="top",
            fontsize=10, style="italic")

for (x1, *_), (x2, *_) in zip(boxes[:-1], boxes[1:]):
    ax.annotate("", xy=(x2 - 0.05, Y + H / 2), xytext=(x1 + W + 0.05, Y + H / 2),
                arrowprops=dict(arrowstyle="->", lw=2.5, color="navy"))

# Small input graph, labels offset above the nodes so they do not overlap
ax.text(1.6, 6.6, "Note Difference Graph Input", ha="center",
        fontsize=12, fontweight="bold")
nodes = {"e1": (0.8, 5.6), "e2": (1.5, 6.0), "e3": (2.2, 5.6), "e4": (2.7, 5.3)}
for a, b in [("e1", "e2"), ("e2", "e3"), ("e1", "e3"), ("e3", "e4")]:
    ax.plot(*zip(nodes[a], nodes[b]), color="grey", lw=1.5, zorder=1)
for name, (x, y) in nodes.items():
    ax.plot(x, y, "o", color=BLUE, markeredgecolor="black", markersize=10, zorder=2)
    ax.text(x, y + 0.25, name, ha="center", fontsize=10)

ax.legend(handles=[Patch(color=c, label=l) for c, l in
                   [(BLUE, "Input Layer"), (GREEN, "Hidden Layers"),
                    (YELLOW, "Pooling Layer"), (RED, "Output Layer")]],
          loc="upper right")

plt.show()
# plt.savefig("Fig6.png", dpi=300, bbox_inches="tight")