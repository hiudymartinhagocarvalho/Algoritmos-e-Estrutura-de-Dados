"""
Interactive graph visualization via Pyvis.
Saves HTML files to output/.
Falls back gracefully when pyvis is not installed.
"""

import os

try:
    from pyvis.network import Network
    _PYVIS = True
except ImportError:
    _PYVIS = False
    print("WARNING: pyvis not installed — visualizations skipped.  Run: pip install pyvis")


# ── coordinate scaling ──────────────────────────────────────────────────────

def _scale(v, lo, hi, out_lo=60, out_hi=940):
    if hi == lo:
        return (out_lo + out_hi) / 2
    return out_lo + (v - lo) / (hi - lo) * (out_hi - out_lo)


def _positions(graph):
    """
    Geographic layout when lat/lon are present; circular layout otherwise.
    """
    import math as _math
    nodes = list(graph.nodes.keys())
    has_coords = all(graph.nodes[n]['lat'] is not None for n in nodes)

    if has_coords:
        lats = [graph.nodes[n]['lat'] for n in nodes]
        lons = [graph.nodes[n]['lon'] for n in nodes]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        pos = {}
        for nid in nodes:
            d = graph.nodes[nid]
            x = _scale(d['lon'],   min_lon,  max_lon)
            y = _scale(-d['lat'], -max_lat, -min_lat)
            pos[nid] = (x, y)
    else:
        # Circular layout for abstract graphs
        n = len(nodes)
        cx, cy, r = 500, 400, 320
        pos = {}
        for i, nid in enumerate(nodes):
            angle = 2 * _math.pi * i / n
            pos[nid] = (cx + r * _math.cos(angle), cy + r * _math.sin(angle))
    return pos


# ── shared network builder ───────────────────────────────────────────────────

def _make_network(directed=False):
    net = Network(height='700px', width='100%', bgcolor='#1a1a2e',
                  font_color='#e0e0e0', directed=directed)
    net.set_options("""{
      "physics": { "enabled": false },
      "edges":   { "font": { "size": 11, "color": "#bbbbbb" } },
      "nodes":   { "font": { "size": 12 } }
    }""")
    return net


# ── public API ───────────────────────────────────────────────────────────────

def visualize_graph(graph, filename='output/graph.html'):
    """Render full graph (no path highlighted)."""
    if not _PYVIS:
        return
    net = _make_network(directed=graph.directed)
    pos = _positions(graph)

    for nid, d in graph.nodes.items():
        x, y = pos[nid]
        has_coords = d['lat'] is not None
        coord_str  = f"<br>lat {d['lat']:.4f}, lon {d['lon']:.4f}" if has_coords else ''
        net.add_node(nid, label=f"{nid}\n{d['name']}", x=x, y=y,
                     color={'background': '#4CAF50', 'border': '#2E7D32'},
                     size=26,
                     title=f"<b>{d['name']}</b>{coord_str}")

    seen = set()
    for u in graph.edges:
        for v, w in graph.edges[u]:
            key = (u, v) if graph.directed else tuple(sorted([u, v]))
            if key not in seen:
                seen.add(key)
                net.add_edge(u, v, label=f"{w}", title=f"weight: {w}",
                             color='#78909C', width=2)

    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    net.save_graph(filename)
    print(f"  [viz] graph          -> {filename}")


def visualize_path(graph, path, algo_name, filename):
    """Render graph with a search path highlighted in red."""
    if not _PYVIS:
        return
    net = _make_network(directed=graph.directed)
    pos = _positions(graph)

    path_set   = set(path) if path else set()
    path_edges = set()
    if path:
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))
            if not graph.directed:
                path_edges.add((path[i + 1], path[i]))

    start_node = path[0]  if path else None
    goal_node  = path[-1] if path else None

    for nid, d in graph.nodes.items():
        x, y = pos[nid]
        if   nid == start_node: col = {'background': '#FF5722', 'border': '#BF360C'}; sz = 32
        elif nid == goal_node:  col = {'background': '#2196F3', 'border': '#0D47A1'}; sz = 32
        elif nid in path_set:   col = {'background': '#FFEB3B', 'border': '#F9A825'}; sz = 26
        else:                   col = {'background': '#4CAF50', 'border': '#2E7D32'}; sz = 20
        net.add_node(nid, label=f"{nid}\n{d['name']}", x=x, y=y,
                     color=col, size=sz, title=f"<b>{d['name']}</b>")

    seen = set()
    for u in graph.edges:
        for v, w in graph.edges[u]:
            key = (u, v) if graph.directed else tuple(sorted([u, v]))
            if key not in seen:
                seen.add(key)
                on = (u, v) in path_edges
                net.add_edge(u, v, label=f"{w}", title=f"weight: {w}",
                             color='#F44336' if on else '#546E7A',
                             width=4 if on else 1)

    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    net.save_graph(filename)
    print(f"  [viz] {algo_name:<12} path -> {filename}")
