import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Create graph
G = nx.DiGraph()

# Add nodes
notes_before = ['N1', 'N2']
rest = ['R']
notes_after = ['N3', 'N4']

G.add_nodes_from(notes_before, node_type='note_before')
G.add_nodes_from(rest, node_type='rest')
G.add_nodes_from(notes_after, node_type='note_after')

# Add consecutive edges
G.add_edge('N1', 'R', edge_type='consecutive')
G.add_edge('N2', 'R', edge_type='consecutive')
G.add_edge('R', 'N3', edge_type='consecutive')
G.add_edge('R', 'N4', edge_type='consecutive')

# Position nodes
pos = {
    'N1': (0, 1),
    'N2': (0, -1),
    'R': (2, 0),
    'N3': (4, 1),
    'N4': (4, -1)
}

# Draw the graph
nx.draw_networkx_nodes(G, pos, nodelist=notes_before + notes_after,
                       node_color='lightblue', node_size=800, ax=ax)
nx.draw_networkx_nodes(G, pos, nodelist=rest,
                       node_color='lightcoral', node_size=800, ax=ax)
nx.draw_networkx_edges(G, pos, edge_color='black',
                       arrows=True, arrowsize=20, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)

ax.set_title('', fontsize=14, fontweight='bold')
ax.axis('off')
ax.set_xlim(-0.5, 4.5)
ax.set_ylim(-2, 2)

# Add legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue',
           markersize=10, label='Note Node'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral',
           markersize=10, label='Rest Node'),
    Line2D([0], [0], color='black', linewidth=2, label='Consecutive Edge')
]
ax.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=11)

plt.tight_layout()
plt.savefig('before_rest_removal.png', dpi=300, bbox_inches='tight')
plt.show()

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# Create graph
G = nx.DiGraph()

# Add only note nodes
notes_before = ['N1', 'N2']
notes_after = ['N3', 'N4']

G.add_nodes_from(notes_before, node_type='note_before')
G.add_nodes_from(notes_after, node_type='note_after')

# Add implied consecutive edges (all before to all after)
for n_before in notes_before:
    for n_after in notes_after:
        G.add_edge(n_before, n_after, edge_type='implied_consecutive')

# Position nodes (remove rest position)
pos = {
    'N1': (0, 1),
    'N2': (0, -1),
    'N3': (4, 1),
    'N4': (4, -1)
}

# Draw the graph
nx.draw_networkx_nodes(G, pos, nodelist=notes_before + notes_after,
                       node_color='lightblue', node_size=800, ax=ax)
nx.draw_networkx_edges(G, pos, edge_color='green', style='dashed',
                       arrows=True, arrowsize=20, ax=ax, width=2)
nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)

ax.set_title('', fontsize=14, fontweight='bold')
ax.axis('off')
ax.set_xlim(-0.5, 4.5)
ax.set_ylim(-2, 2)

# Add legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue',
           markersize=10, label='Note Node'),
    Line2D([0], [0], color='green', linewidth=2, linestyle='--',
           label='Implied Consecutive Edge')
]
ax.legend(handles=legend_elements, loc='lower center', ncol=2, fontsize=11)

plt.tight_layout()
plt.savefig('after_rest_removal.png', dpi=300, bbox_inches='tight')
plt.show()