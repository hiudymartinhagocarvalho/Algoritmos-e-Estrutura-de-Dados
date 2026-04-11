"""
Loaders for real-world network datasets.

Congress Twitter Network
  Source: Fink et al. (2023) — weighted directed influence network
  among US Congress members on Twitter.
  Edge weight = transmission probability (0–1).
  Stored cost = 1 / probability  (lower prob → higher cost).

P2P Gnutella Network
  Source: SNAP — directed peer-to-peer overlay (August 2002).
  Edge weight = 1 (hop count).

Both loaders extract a 12-node subgraph to satisfy the assignment
requirement of 10–15 nodes.  Because nodes carry no geographic
coordinates, the heuristic h(n)=0 is used — trivially admissible.
"""

import os
import json
import ast
from collections import defaultdict, deque
from graph import Graph


# ── Congress ──────────────────────────────────────────────────────────────────

def _read_congress_edges(filepath):
    """
    Parse 'u v {"weight": x}' lines from congress.edgelist.
    Returns (edges, degree_counter).
    """
    edges = []
    degree = defaultdict(int)
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(maxsplit=2)
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            weight = 1.0
            if len(parts) == 3:
                try:
                    data = ast.literal_eval(parts[2])
                    weight = float(data.get('weight', 1.0))
                except Exception:
                    pass
            edges.append((u, v, weight))
            degree[u] += 1
            degree[v] += 1
    return edges, degree


def load_congress_subgraph(edgelist_path, json_path=None, n=12):
    """
    Extract an n-node subgraph from the Congressional Twitter influence network.

    Strategy: pick the n most-connected Congress members (highest total degree),
    keep all directed edges between them.
    Cost = round(1 / probability, 4)  — high-influence links cost less.

    Parameters
    ----------
    edgelist_path : str   path to congress.edgelist
    json_path     : str   path to congress_network_data.json (for usernames)
    n             : int   number of nodes (10–15)

    Returns
    -------
    Graph (directed=True, no geographic coords)
    """
    edges, degree = _read_congress_edges(edgelist_path)

    # Top-n nodes by total (in + out) degree
    top_nodes = set(sorted(degree, key=lambda x: -degree[x])[:n])

    # Load Twitter usernames if JSON is available
    usernames = {}
    if json_path and os.path.exists(json_path):
        with open(json_path, encoding='utf-8') as f:
            raw = json.load(f)
        data = raw[0] if isinstance(raw, list) else raw
        for i, uname in enumerate(data.get('usernameList', [])):
            if i in top_nodes:
                usernames[i] = uname

    g = Graph(directed=True)
    for node in sorted(top_nodes):
        label = usernames.get(node, f'Rep{node}')
        g.add_node(str(node), label)         # no lat/lon → h=0 fallback

    seen = set()
    for u, v, w in edges:
        if u in top_nodes and v in top_nodes:
            key = (u, v)
            if key not in seen:
                seen.add(key)
                cost = round(1.0 / max(w, 1e-9), 4)
                g.add_edge(str(u), str(v), cost)

    return g


# ── Congress full graph ───────────────────────────────────────────────────────

def load_congress_full_graph(json_path, edgelist_path=None):
    """
    Load the COMPLETE Congress Twitter network combining both data sources.

    - congress_network_data.json  →  node names (usernameList)
    - congress.edgelist           →  edge connections and weights
      (falls back to outList/outWeight from JSON when edgelist_path is None)

    Edge cost = 1 / transmission_probability  (high influence = low cost).
    Returns a directed Graph with all 475 nodes (no geographic coords → h=0).
    """
    with open(json_path, encoding='utf-8') as f:
        raw = json.load(f)
    data      = raw[0] if isinstance(raw, list) else raw
    usernames = data.get('usernameList', [])
    n_nodes   = len(data['outList'])

    g = Graph(directed=True)
    for i in range(n_nodes):
        label = usernames[i] if i < len(usernames) else f'Rep{i}'
        g.add_node(str(i), label)

    if edgelist_path and os.path.exists(edgelist_path):
        # Primary source: congress.edgelist (explicit edge list with weights)
        edges, _ = _read_congress_edges(edgelist_path)
        for u, v, w in edges:
            cost = round(1.0 / max(w, 1e-9), 4)
            g.add_edge(str(u), str(v), cost)
    else:
        # Fallback: outList / outWeight from JSON
        for i, targets in enumerate(data['outList']):
            for j, target in enumerate(targets):
                w    = data['outWeight'][i][j]
                cost = round(1.0 / max(w, 1e-9), 4)
                g.add_edge(str(i), str(target), cost)

    return g


# ── P2P Gnutella ──────────────────────────────────────────────────────────────

def _read_p2p_edges(filepath):
    """
    Parse 'u v [weight]' lines, ignoring comment lines (#).
    Returns (adjacency_dict, degree_counter).
    """
    adj    = defaultdict(list)
    degree = defaultdict(int)
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            u, v = int(parts[0]), int(parts[1])
            w = float(parts[2]) if len(parts) >= 3 else 1.0
            adj[u].append((v, w))
            degree[u] += 1
            degree[v] += 1
    return adj, degree


def load_p2p_subgraph(filepath, n=12):
    """
    Extract an n-node BFS-connected subgraph from the P2P Gnutella network.

    Strategy: seed BFS from the highest-degree peer; take the first n nodes
    reached.  All edges among them are kept.  Weight = 1 (hop count).

    Parameters
    ----------
    filepath : str   path to p2p-Gnutella08.txt
    n        : int   number of nodes (10–15)

    Returns
    -------
    Graph (directed=True, no geographic coords)
    """
    adj, degree = _read_p2p_edges(filepath)

    # Start from the most-connected peer
    seed = max(degree, key=lambda x: degree[x])

    # BFS to collect n reachable nodes
    visited_order, seen_bfs = [], {seed}
    queue = deque([seed])
    while queue and len(visited_order) < n:
        node = queue.popleft()
        visited_order.append(node)
        for nbr, _ in adj[node]:
            if nbr not in seen_bfs:
                seen_bfs.add(nbr)
                queue.append(nbr)

    subgraph_nodes = set(visited_order)

    g = Graph(directed=True)
    for node in sorted(subgraph_nodes):
        g.add_node(str(node), f'Peer {node}')   # no lat/lon → h=0 fallback

    seen_edges = set()
    for u in subgraph_nodes:
        for v, w in adj[u]:
            if v in subgraph_nodes and (u, v) not in seen_edges:
                seen_edges.add((u, v))
                g.add_edge(str(u), str(v), w)

    return g


# ── Test-pair helper ──────────────────────────────────────────────────────────

def find_reachable_pairs(graph, n_pairs=5):
    """
    Return n_pairs of (start, goal) that have a directed path in graph.
    Uses BFS reachability from each candidate start node.
    """
    nodes = list(graph.nodes.keys())
    pairs, tried = [], set()

    for start in nodes:
        if len(pairs) >= n_pairs:
            break
        # BFS from start
        reachable, vis = [], {start}
        q = deque([start])
        while q:
            n = q.popleft()
            for nbr, _ in graph.get_neighbors(n):
                if nbr not in vis:
                    vis.add(nbr)
                    reachable.append(nbr)
                    q.append(nbr)
        # Prefer distant goals (end of reachable list)
        for goal in reversed(reachable):
            if (start, goal) not in tried:
                tried.add((start, goal))
                pairs.append((start, goal))
                if len(pairs) >= n_pairs:
                    break

    return pairs
