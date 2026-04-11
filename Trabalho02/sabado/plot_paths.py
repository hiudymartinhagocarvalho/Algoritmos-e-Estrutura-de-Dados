"""
Matplotlib path visualization for search algorithms.
Uses NetworkX only for spring_layout — all search logic uses our own algorithms.
"""

import os
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

BG    = '#0d0d0d'
PANEL = '#111111'

ALGO_COLORS = {
    'Dijkstra': '#2196F3',
    'Greedy':   '#FF9800',
    'A*':       '#9C27B0',
    'DFS':      '#4CAF50',
    'BFS':      '#00BCD4',
}


# ── graph helpers ─────────────────────────────────────────────────────────────

def find_target(g):
    """Return node with highest out-degree (most connected → red node)."""
    return max(g.nodes, key=lambda n: len(g.edges[n]))


def find_source(g, target):
    """Return least-connected node that can reach target via BFS."""
    def _reachable(start, goal):
        vis, q = {start}, deque([start])
        while q:
            n = q.popleft()
            if n == goal:
                return True
            for nbr, _ in g.get_neighbors(n):
                if nbr not in vis:
                    vis.add(nbr); q.append(nbr)
        return False

    for n in sorted(g.nodes, key=lambda x: len(g.edges[x])):
        if n != target and _reachable(n, target):
            return n
    return None


# ── internal drawing helpers ──────────────────────────────────────────────────

def _build_layout(g):
    G_nx = nx.DiGraph()
    for nid in g.nodes:
        G_nx.add_node(int(nid))
    for u in g.edges:
        for v, _ in g.edges[u]:
            G_nx.add_edge(int(u), int(v))
    pos = nx.spring_layout(G_nx, k=1.5, iterations=80, seed=42)
    return G_nx, pos


def _node_props(nid_int, path_set, color, source, target):
    s = str(nid_int)
    if s == target:  return '#FF0000', 300
    if s == source:  return '#FFEB3B', 220
    if nid_int in path_set: return color, 100
    return '#2b2b2b', 6


def _legend(ax, g, source, target):
    handles = [
        mpatches.Patch(color='#FF0000', label=f"Target: {g.nodes[target]['name']}"),
        mpatches.Patch(color='#FFEB3B', label=f"Source: {g.nodes[source]['name']}"),
    ] + [mpatches.Patch(color=c, label=a) for a, c in ALGO_COLORS.items()]
    ax.legend(handles=handles, loc='lower center',
              facecolor='#1a1a1a', edgecolor='#444444',
              labelcolor='white', fontsize=8,
              bbox_to_anchor=(0.5, -0.02), ncol=4)


def _save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  Saved → {path}")


# ── public API ────────────────────────────────────────────────────────────────

def generate_path_plots(g, source, target, results, out_dir):
    """
    Save one PNG per algorithm + one overview PNG.

    Parameters
    ----------
    g        : Graph  (full graph)
    source   : str    start node ID
    target   : str    goal node ID  (red node)
    results  : dict   algo_name -> {'path', 'cost', 'expanded'}
    out_dir  : str    output folder
    """
    os.makedirs(out_dir, exist_ok=True)
    print("\n[plot] Computing spring layout...")
    G_nx, pos = _build_layout(g)
    node_ids  = list(G_nx.nodes())

    # ── overview ──────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
    ax.set_facecolor(PANEL)

    colors0 = ['#FF0000' if str(n) == target
               else '#FFEB3B' if str(n) == source
               else '#1e3a5f' for n in node_ids]
    sizes0  = [300 if str(n) == target
               else 220 if str(n) == source
               else 8 for n in node_ids]

    nx.draw_networkx_nodes(G_nx, pos, node_color=colors0, node_size=sizes0, ax=ax)
    nx.draw_networkx_edges(G_nx, pos, alpha=0.04,
                           edge_color='#666666', arrows=False, ax=ax)
    nx.draw_networkx_labels(G_nx, pos,
                            labels={int(target): g.nodes[target]['name'],
                                    int(source): g.nodes[source]['name']},
                            font_size=7, font_color='white', ax=ax)
    ax.set_title(
        f"{g.num_nodes} nodes · {g.num_edges} edges\n"
        f"Source (yellow): {g.nodes[source]['name']}\n"
        f"Target  (red)  : {g.nodes[target]['name']}",
        color='white', fontsize=9
    )
    ax.axis('off')
    _legend(ax, g, source, target)
    fig.suptitle("US Congress Twitter Influence Network — Overview",
                 color='white', fontsize=12, fontweight='bold')
    plt.tight_layout()
    _save(fig, os.path.join(out_dir, 'congress_00_overview.png'))

    # ── one image per algorithm ───────────────────────────────────────────────
    for algo_name, res in results.items():
        path, cost, expanded = res['path'], res['cost'], res['expanded']
        color      = ALGO_COLORS.get(algo_name, '#ffffff')
        path_set   = set(int(p) for p in path) if path else set()
        path_edges = [(int(path[i]), int(path[i+1]))
                      for i in range(len(path)-1)] if path else []

        fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG)
        ax.set_facecolor(PANEL)

        nc, ns = zip(*[_node_props(n, path_set, color, source, target)
                       for n in node_ids])
        nx.draw_networkx_nodes(G_nx, pos, node_color=list(nc),
                               node_size=list(ns), ax=ax, alpha=0.95)
        nx.draw_networkx_edges(G_nx, pos, alpha=0.04,
                               edge_color='#555555', arrows=False, ax=ax)

        if path_edges:
            nx.draw_networkx_edges(G_nx, pos, edgelist=path_edges,
                                   edge_color=color, width=2.5,
                                   arrows=True, arrowsize=14,
                                   connectionstyle='arc3,rad=0.15', ax=ax)
        if path:
            label_set = path_set | {int(source), int(target)}
            nx.draw_networkx_labels(G_nx, pos,
                                    labels={n: g.nodes[str(n)]['name']
                                            for n in label_set
                                            if str(n) in g.nodes},
                                    font_size=6, font_color='white', ax=ax)

        path_str = (' → '.join(g.nodes[p]['name'] for p in path)
                    if path else 'NOT FOUND')
        if len(path_str) > 65:
            path_str = path_str[:62] + '...'

        ax.set_title(
            f"{algo_name}\n"
            f"Cost: {cost:.2f}  |  Nodes expanded: {expanded}\n"
            f"{path_str}",
            color='white', fontsize=8.5
        )
        ax.axis('off')
        _legend(ax, g, source, target)
        fig.suptitle(
            f"US Congress Twitter Influence Network — {algo_name}",
            color='white', fontsize=12, fontweight='bold'
        )
        plt.tight_layout()
        safe = algo_name.lower().replace('*', 'star').replace(' ', '_')
        _save(fig, os.path.join(out_dir, f'congress_{safe}.png'))
