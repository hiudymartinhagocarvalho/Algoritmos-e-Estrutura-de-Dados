"""
Search Algorithm Path Visualization — US Congress Twitter Influence Network

Loads the complete Congress network, finds the most-connected node (red),
picks a reachable source, runs all 5 algorithms and plots one subplot per
algorithm showing the path taken to reach the red node.
"""

import os
import sys
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx          # used ONLY for spring_layout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_loaders import load_congress_full_graph
from algorithms    import dijkstra, greedy_best_first, a_star, dfs, bfs

# ── paths ─────────────────────────────────────────────────────────────────────
_HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(_HERE, '..', '..', 'projetos', 'Trabalho02')
JSON_PATH = os.path.join(DATA_DIR, 'congress_network_data.json')
OUT_DIR   = os.path.join(_HERE, 'output')
os.makedirs(OUT_DIR, exist_ok=True)

# ── load full graph ───────────────────────────────────────────────────────────
print("Loading Congress network...")
g = load_congress_full_graph(JSON_PATH)
print(f"  {g.num_nodes} nodes, {g.num_edges} edges")

# ── find most-connected node (TARGET = red node) ──────────────────────────────
out_degree = {nid: len(g.edges[nid]) for nid in g.nodes}
target     = max(out_degree, key=lambda x: out_degree[x])
print(f"  Target (red) : {g.nodes[target]['name']}  "
      f"(out-degree = {out_degree[target]})")

# ── find source: least-connected node that can reach target ───────────────────
def _can_reach(graph, start, goal):
    vis = {start}
    q   = deque([start])
    while q:
        n = q.popleft()
        if n == goal:
            return True
        for nbr, _ in graph.get_neighbors(n):
            if nbr not in vis:
                vis.add(nbr)
                q.append(nbr)
    return False

source = None
for n in sorted(out_degree, key=lambda x: out_degree[x]):
    if n != target and _can_reach(g, n, target):
        source = n
        break

print(f"  Source (yellow): {g.nodes[source]['name']}  "
      f"(out-degree = {out_degree[source]})")

# ── run all 5 algorithms ──────────────────────────────────────────────────────
ALGORITHMS = {
    'Dijkstra': dijkstra,
    'Greedy':   greedy_best_first,
    'A*':       a_star,
    'DFS':      dfs,
    'BFS':      bfs,
}
ALGO_COLORS = {
    'Dijkstra': '#2196F3',
    'Greedy':   '#FF9800',
    'A*':       '#9C27B0',
    'DFS':      '#4CAF50',
    'BFS':      '#00BCD4',
}

results = {}
print(f"\nSearching: {g.nodes[source]['name']} → {g.nodes[target]['name']}")
for name, func in ALGORITHMS.items():
    path, cost, expanded = func(g, source, target)
    results[name] = {'path': path, 'cost': cost, 'expanded': expanded}
    names = ' → '.join(g.nodes[p]['name'] for p in path) if path else 'NOT FOUND'
    print(f"  {name:<10} cost={cost:>10.2f}  expanded={expanded:>4}  "
          f"path={names[:70]}{'...' if len(names) > 70 else ''}")

# ── build NetworkX graph for spring layout only ───────────────────────────────
print("\nComputing spring layout...")
G_nx = nx.DiGraph()
for nid in g.nodes:
    G_nx.add_node(int(nid))
for u in g.edges:
    for v, _ in g.edges[u]:
        G_nx.add_edge(int(u), int(v))

pos      = nx.spring_layout(G_nx, k=1.5, iterations=80, seed=42)
node_ids = list(G_nx.nodes())

# ── draw helpers ──────────────────────────────────────────────────────────────
BG     = '#0d0d0d'
PANEL  = '#111111'

def _node_style(nid_int, path_set, color):
    s = str(nid_int)
    if s == target:
        return '#FF0000', 300
    if s == source:
        return '#FFEB3B', 220
    if nid_int in path_set:
        return color, 100
    return '#2b2b2b', 6


def draw_overview(ax):
    ax.set_facecolor(PANEL)
    n_colors = ['#FF0000' if str(n) == target
                else '#FFEB3B' if str(n) == source
                else '#1e3a5f'
                for n in node_ids]
    n_sizes  = [300 if str(n) == target
                else 220 if str(n) == source
                else 8 for n in node_ids]

    nx.draw_networkx_nodes(G_nx, pos, node_color=n_colors,
                           node_size=n_sizes, ax=ax)
    nx.draw_networkx_edges(G_nx, pos, alpha=0.04,
                           edge_color='#666666', arrows=False, ax=ax)
    nx.draw_networkx_labels(G_nx, pos,
                            labels={int(target): g.nodes[target]['name'],
                                    int(source): g.nodes[source]['name']},
                            font_size=7, font_color='white', ax=ax)
    ax.set_title(
        f"US Congress Twitter Network\n"
        f"{g.num_nodes} nodes · {g.num_edges} edges\n"
        f"Source (yellow): {g.nodes[source]['name']}\n"
        f"Target  (red)  : {g.nodes[target]['name']}",
        color='white', fontsize=9, pad=6
    )
    ax.axis('off')


def draw_algo(ax, algo_name, path, cost, expanded):
    ax.set_facecolor(PANEL)
    color    = ALGO_COLORS[algo_name]
    path_set = set(int(p) for p in path) if path else set()

    n_colors, n_sizes = zip(*[_node_style(n, path_set, color) for n in node_ids])

    nx.draw_networkx_nodes(G_nx, pos, node_color=list(n_colors),
                           node_size=list(n_sizes), ax=ax, alpha=0.95)
    nx.draw_networkx_edges(G_nx, pos, alpha=0.04,
                           edge_color='#555555', arrows=False, ax=ax)

    if path:
        path_edges = [(int(path[i]), int(path[i + 1]))
                      for i in range(len(path) - 1)]
        nx.draw_networkx_edges(G_nx, pos, edgelist=path_edges,
                               edge_color=color, width=2.5, arrows=True,
                               arrowsize=14,
                               connectionstyle='arc3,rad=0.15', ax=ax)
        label_nodes = path_set | {int(source), int(target)}
        nx.draw_networkx_labels(
            G_nx, pos,
            labels={n: g.nodes[str(n)]['name']
                    for n in label_nodes if str(n) in g.nodes},
            font_size=6, font_color='white', ax=ax
        )

    path_str = (' → '.join(g.nodes[p]['name'] for p in path)
                if path else 'NOT FOUND')
    if len(path_str) > 65:
        path_str = path_str[:62] + '...'

    ax.set_title(
        f"{algo_name}\n"
        f"Cost: {cost:.2f}  |  Nodes expanded: {expanded}\n"
        f"{path_str}",
        color='white', fontsize=8.5, pad=6
    )
    ax.axis('off')


# ── save each figure separately ──────────────────────────────────────────────

def _legend(ax):
    handles = [
        mpatches.Patch(color='#FF0000', label=f"Target: {g.nodes[target]['name']}"),
        mpatches.Patch(color='#FFEB3B', label=f"Source: {g.nodes[source]['name']}"),
    ] + [mpatches.Patch(color=ALGO_COLORS[a], label=a) for a in ALGORITHMS]
    ax.legend(handles=handles, loc='lower center',
              facecolor='#1a1a1a', edgecolor='#444444',
              labelcolor='white', fontsize=8,
              bbox_to_anchor=(0.5, -0.02), ncol=4)


def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  Saved → {path}")


print("\nGenerating images...")

# 1. Overview
fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
draw_overview(ax)
_legend(ax)
fig.suptitle("US Congress Twitter Influence Network — Overview",
             color='white', fontsize=12, fontweight='bold')
plt.tight_layout()
save_fig(fig, 'congress_00_overview.png')

# 2-6. One image per algorithm
for algo_name, res in results.items():
    fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
    draw_algo(ax, algo_name, res['path'], res['cost'], res['expanded'])
    _legend(ax)
    fig.suptitle(
        f"US Congress Twitter Influence Network — {algo_name}",
        color='white', fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    safe = algo_name.lower().replace('*', 'star').replace(' ', '_')
    save_fig(fig, f'congress_{safe}.png')

print("Done.")

# open all images
import subprocess
for f in sorted(os.listdir(OUT_DIR)):
    if f.startswith('congress_') and f.endswith('.png'):
        subprocess.Popen(['open', os.path.join(OUT_DIR, f)])
