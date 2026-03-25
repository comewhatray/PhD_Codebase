import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Define layer positions and sizes
layer_width = 1.5
layer_height = 0.8
spacing = 2.5

# Layer positions (x, y)
positions = [
    (1, 4),  # Input Layer
    (4.5, 4),  # Hidden Layer 1
    (8, 4),  # Hidden Layer 2
    (11.5, 2.5),  # Global Mean Pooling
    (11.5, 0.5)  # Linear Output
]

# Layer labels and details
layers = [
    ("GraphSAGE\nConvolutional\n(Input)", "Input: 3 features\n(pitch diff, onset diff, temporal gap)", 'lightblue'),
    ("GraphSAGE\nConvolutional\n(Hidden 1)", "Hidden: 75 dimensions\nReLU activation\nDropout: 0.2", 'lightgreen'),
    ("GraphSAGE\nConvolutional\n(Hidden 2)", "Hidden: 75 dimensions\nReLU activation\nDropout: 0.2", 'lightgreen'),
    ("Global Mean\nPooling", "Aggregates node-level\nrepresentations to\ngraph-level", 'lightyellow'),
    ("Linear\nOutput", "Output: 5 classes\n(Composer probabilities)", 'lightcoral')
]

# Draw layers
for i, ((x, y), (title, description, color)) in enumerate(zip(positions, layers)):
    # Main layer box
    layer_box = FancyBboxPatch((x - layer_width / 2, y - layer_height / 2),
                               layer_width, layer_height,
                               boxstyle="round,pad=0.1",
                               facecolor=color,
                               edgecolor='black',
                               linewidth=2)
    ax.add_patch(layer_box)

    # Layer title
    ax.text(x, y, title, ha='center', va='center',
            fontsize=10, fontweight='bold', wrap=True)

    # Description below
    ax.text(x, y - 1.2, description, ha='center', va='center',
            fontsize=8, style='italic')

# Draw arrows between layers
arrow_props = dict(arrowstyle='->', lw=2, color='darkblue')

# Input to Hidden 1
ax.annotate('', xy=(positions[1][0] - layer_width / 2, positions[1][1]),
            xytext=(positions[0][0] + layer_width / 2, positions[0][1]),
            arrowprops=arrow_props)

# Hidden 1 to Hidden 2
ax.annotate('', xy=(positions[2][0] - layer_width / 2, positions[2][1]),
            xytext=(positions[1][0] + layer_width / 2, positions[1][1]),
            arrowprops=arrow_props)

# Hidden 2 to Pooling
ax.annotate('', xy=(positions[3][0] - layer_width / 2, positions[3][1] + layer_height / 4),
            xytext=(positions[2][0] + layer_width / 2, positions[2][1]),
            arrowprops=arrow_props)

# Pooling to Output
ax.annotate('', xy=(positions[4][0], positions[4][1] + layer_height / 2),
            xytext=(positions[3][0], positions[3][1] - layer_height / 2),
            arrowprops=arrow_props)

# Add graph representation on the left
graph_x, graph_y = 1, 6.5
ax.text(graph_x, graph_y, 'Note Difference Graph\nInput',
        ha='center', va='center', fontsize=12, fontweight='bold')

# Simple graph visualization
node_positions = [(0.2, 6), (0.8, 6.2), (1.4, 6), (1.8, 5.8)]
for i, (nx, ny) in enumerate(node_positions):
    circle = plt.Circle((nx, ny), 0.08, color='lightblue', ec='black')
    ax.add_patch(circle)
    ax.text(nx, ny, f'e{i + 1}', ha='center', va='center', fontsize=8)

# Add some edges
edges = [(0, 1), (1, 2), (2, 3), (0, 2)]
for i, j in edges:
    x1, y1 = node_positions[i]
    x2, y2 = node_positions[j]
    ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.6, linewidth=1)

# Add title
ax.set_title('Graph Neural Network Architecture for Era Classification',
             fontsize=16, fontweight='bold', pad=20)

# Add legend
legend_elements = [
    mpatches.Patch(color='lightblue', label='Input Layer'),
    mpatches.Patch(color='lightgreen', label='Hidden Layers'),
    mpatches.Patch(color='lightyellow', label='Pooling Layer'),
    mpatches.Patch(color='lightcoral', label='Output Layer')
]
ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))

# Set axis properties
ax.set_xlim(-0.5, 13.5)
ax.set_ylim(-0.5, 7.5)
ax.axis('off')

plt.tight_layout()
plt.savefig('gnn_architecture.png', dpi=300, bbox_inches='tight')
plt.show()