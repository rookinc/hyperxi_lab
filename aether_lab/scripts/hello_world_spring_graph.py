import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edges_from([
    ("Hello", "World"),
    ("Hello", "Spring"),
    ("Spring", "Layout"),
    ("Layout", "PNG"),
    ("World", "PNG")
])

pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(8, 6))
nx.draw_networkx(
    G,
    pos,
    with_labels=True,
    node_size=2200,
    font_size=12
)

plt.axis("off")
plt.tight_layout()
plt.savefig("hello_world_spring_graph.png", dpi=200, bbox_inches="tight")
print("saved hello_world_spring_graph.png")
