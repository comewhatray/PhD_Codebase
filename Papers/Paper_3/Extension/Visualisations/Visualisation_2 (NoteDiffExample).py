import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

fig = plt.figure(figsize=(14, 6))

# Create two subplots
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

# ===== LEFT SIDE: Original Graph (Szeto & Wong) =====
G1 = nx.Graph()
notes = ['N1', 'N2', 'N3', 'N4']
edges = [('N1', 'N2'), ('N2', 'N3'), ('N2', 'N4'), ('N3', 'N4')]

G1.add_nodes_from(notes)
G1.add_edges_from(edges)

pos1 = {
    'N1': (0, 1),
    'N2': (2, 1),
    'N3': (2, -1),
    'N4': (4, 0)
}

# Draw original graph
nx.draw_networkx_nodes(G1, pos1, node_color='lightblue',
                       node_size=1200, ax=ax1)
nx.draw_networkx_labels(G1, pos1, font_size=14,
                        font_weight='bold', ax=ax1)
nx.draw_networkx_edges(G1, pos1, width=2, ax=ax1)

# Add edge labels
edge_labels = {
    ('N1', 'N2'): 'e1',
    ('N2', 'N3'): 'e2',
    ('N2', 'N4'): 'e3',
    ('N3', 'N4'): 'e4'
}
nx.draw_networkx_edge_labels(G1, pos1, edge_labels,
                             font_size=11, font_color='red', ax=ax1)

ax1.set_title('Original Graph\n(Nodes = Notes, Edges = Relationships)',
              fontsize=13, fontweight='bold', pad=10)
ax1.axis('off')
ax1.set_xlim(-0.5, 4.5)
ax1.set_ylim(-2, 2)

# ===== RIGHT SIDE: Note Difference Graph =====
G2 = nx.Graph()
edge_nodes = ['e1', 'e2', 'e3', 'e4']
diff_edges = [('e1', 'e2'), ('e1', 'e3'), ('e2', 'e3'),
              ('e2', 'e4'), ('e3', 'e4')]

G2.add_nodes_from(edge_nodes)
G2.add_edges_from(diff_edges)

pos2 = {
    'e1': (1, 1.5),
    'e2': (0, 0),
    'e3': (2, 0),
    'e4': (1, -1.5)
}

# Draw note difference graph
nx.draw_networkx_nodes(G2, pos2, node_color='lightcoral',
                       node_size=1200, ax=ax2)
nx.draw_networkx_labels(G2, pos2, font_size=14,
                        font_weight='bold', ax=ax2)
nx.draw_networkx_edges(G2, pos2, width=2, style='dashed',
                       edge_color='green', ax=ax2)

ax2.set_title('Note Difference Graph\n(Nodes = Original Edges, Edges = Shared Notes)',
              fontsize=13, fontweight='bold', pad=10)
ax2.axis('off')
ax2.set_xlim(-1, 3)
ax2.set_ylim(-2.5, 2.5)

# Add legend
legend_elements = [
    mpatches.Circle((0, 0), 0.1, facecolor='lightblue',
                    edgecolor='black', label='Note (Original)'),
    mpatches.Circle((0, 0), 0.1, facecolor='lightcoral',
                    edgecolor='black', label='Edge/Relationship (Note Diff.)'),
    plt.Line2D([0], [0], color='black', linewidth=2,
               label='Relationship (Original)'),
    plt.Line2D([0], [0], color='green', linewidth=2,
               linestyle='--', label='Shared Note (Note Diff.)')
]

fig.legend(handles=legend_elements, loc='lower center',
          ncol=2, bbox_to_anchor=(0.5, -0.05), fontsize=11)

plt.tight_layout()
plt.savefig('note_difference_graph_demo.png', dpi=300,
            bbox_inches='tight', pad_inches=0.3)
plt.show()