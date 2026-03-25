import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

fig = plt.figure(figsize=(16, 8))

# Create two subplots
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

# ===== LEFT SIDE: Original Graph (More realistic example) =====
G1 = nx.Graph()
notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4']
edges = [('C4', 'D4'), ('D4', 'E4'), ('E4', 'F4'), ('F4', 'G4'),
         ('G4', 'A4'), ('C4', 'E4'), ('D4', 'F4'), ('E4', 'G4'),
         ('F4', 'A4'), ('C4', 'G4')]

G1.add_nodes_from(notes)
G1.add_edges_from(edges)

pos1 = {
    'C4': (0, 2),
    'D4': (2, 2),
    'E4': (4, 2),
    'F4': (1, 0),
    'G4': (3, 0),
    'A4': (2, -1)
}

# Draw original graph
nx.draw_networkx_nodes(G1, pos1, node_color='lightblue',
                       node_size=1500, ax=ax1)
nx.draw_networkx_labels(G1, pos1, font_size=12,
                        font_weight='bold', ax=ax1)
nx.draw_networkx_edges(G1, pos1, width=2, ax=ax1)

# Add edge labels for original graph
edge_labels = {
    ('C4', 'D4'): 'e1', ('D4', 'E4'): 'e2', ('E4', 'F4'): 'e3',
    ('F4', 'G4'): 'e4', ('G4', 'A4'): 'e5', ('C4', 'E4'): 'e6',
    ('D4', 'F4'): 'e7', ('E4', 'G4'): 'e8', ('F4', 'A4'): 'e9',
    ('C4', 'G4'): 'e10'
}
nx.draw_networkx_edge_labels(G1, pos1, edge_labels,
                             font_size=9, font_color='red', ax=ax1)

ax1.set_title('Original Graph\n6 Notes, 10 Edges',
              fontsize=14, fontweight='bold', pad=15)
ax1.axis('off')
ax1.set_xlim(-0.8, 4.8)
ax1.set_ylim(-1.8, 2.8)

# ===== RIGHT SIDE: Note Difference Graph =====
G2 = nx.Graph()
edge_nodes = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'e10']

# Create connections between edges that share notes
# e1(C4-D4) connects to: e2(D4-E4), e6(C4-E4), e7(D4-F4), e10(C4-G4)
# e2(D4-E4) connects to: e1(C4-D4), e3(E4-F4), e6(C4-E4), e7(D4-F4), e8(E4-G4)
# etc.
diff_edges = [
    # e1 connections (shares C4 or D4)
    ('e1', 'e2'), ('e1', 'e6'), ('e1', 'e7'), ('e1', 'e10'),
    # e2 connections (shares D4 or E4)
    ('e2', 'e3'), ('e2', 'e6'), ('e2', 'e7'), ('e2', 'e8'),
    # e3 connections (shares E4 or F4)
    ('e3', 'e4'), ('e3', 'e6'), ('e3', 'e7'), ('e3', 'e8'), ('e3', 'e9'),
    # e4 connections (shares F4 or G4)
    ('e4', 'e5'), ('e4', 'e7'), ('e4', 'e8'), ('e4', 'e9'), ('e4', 'e10'),
    # e5 connections (shares G4 or A4)
    ('e5', 'e8'), ('e5', 'e9'), ('e5', 'e10'),
    # e6 connections (shares C4 or E4) - already covered above
    # e7 connections (shares D4 or F4) - already covered above
    # e8 connections (shares E4 or G4)
    ('e8', 'e9'), ('e8', 'e10'),
    # e9 connections (shares F4 or A4) - already covered above
    # e10 connections (shares C4 or G4) - already covered above
]

G2.add_nodes_from(edge_nodes)
G2.add_edges_from(diff_edges)

# Position nodes in a more spread out layout
pos2 = {
    'e1': (0, 2),
    'e2': (2, 2.5),
    'e3': (4, 2),
    'e4': (4, 0),
    'e5': (3, -1),
    'e6': (0, 0.5),
    'e7': (1, 1),
    'e8': (3, 1),
    'e9': (2, -0.5),
    'e10': (1, -1)
}

# Draw note difference graph
nx.draw_networkx_nodes(G2, pos2, node_color='lightcoral',
                       node_size=1200, ax=ax2)
nx.draw_networkx_labels(G2, pos2, font_size=10,
                        font_weight='bold', ax=ax2)
nx.draw_networkx_edges(G2, pos2, width=1.5, style='dashed',
                       edge_color='green', alpha=0.7, ax=ax2)

ax2.set_title('Note Difference Graph\n10 Nodes, 25 Edges',
              fontsize=14, fontweight='bold', pad=15)
ax2.axis('off')
ax2.set_xlim(-0.8, 4.8)
ax2.set_ylim(-1.8, 3)

# Add transformation arrow between plots
arrow = FancyArrowPatch((5.2, 0.5), (6.8, 0.5),
                       connectionstyle="arc3",
                       arrowstyle='->',
                       mutation_scale=25,
                       color='darkblue',
                       linewidth=3)
fig.patches.append(arrow)

# Add "TRANSFORM" text
fig.text(0.5, 0.55, 'TRANSFORM', ha='center', va='center',
         fontsize=14, fontweight='bold', color='darkblue',
         bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))

# Add legend
legend_elements = [
    mpatches.Circle((0, 0), 0.1, facecolor='lightblue',
                    edgecolor='black', label='MIDI Note'),
    mpatches.Circle((0, 0), 0.1, facecolor='lightcoral',
                    edgecolor='black', label='Note Relationship'),
    plt.Line2D([0], [0], color='black', linewidth=2,
               label='Note Connection'),
    plt.Line2D([0], [0], color='green', linewidth=2,
               linestyle='--', label='Shared Note Connection', alpha=0.7)
]

fig.legend(handles=legend_elements, loc='lower center',
          ncol=2, bbox_to_anchor=(0.5, -0.02), fontsize=11)

# # Add explanation text
# fig.text(0.5, 0.02,
#          'Density Increase: 6 notes → 10 relationships → 25 connections\n'
#          'Each original edge becomes a node; nodes connect when sharing a common note',
#          ha='center', va='bottom', fontsize=12, style='italic',
#          bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgray', alpha=0.6))

plt.tight_layout()
plt.subplots_adjust(bottom=0.15)
plt.savefig('detailed_note_difference_transformation.png', dpi=300,
            bbox_inches='tight', pad_inches=0.3)
plt.show()