"""
Graph module — supports geographic (Curitiba) and abstract (Congress, P2P) networks.
Coordinates are optional; when absent the heuristic returns 0 (trivially admissible).
Supports both undirected (default) and directed graphs.
"""
import math


class Graph:
    def __init__(self, directed=False):
        self.nodes = {}      # id -> {'name', 'lat'|None, 'lon'|None}
        self.edges = {}      # id -> [(neighbor_id, weight), ...]
        self.directed = directed

    def add_node(self, node_id, name, lat=None, lon=None):
        self.nodes[node_id] = {'name': name, 'lat': lat, 'lon': lon}
        self.edges[node_id] = []

    def add_edge(self, u, v, weight):
        self.edges[u].append((v, weight))
        if not self.directed:
            self.edges[v].append((u, weight))

    def get_neighbors(self, node_id):
        return self.edges.get(node_id, [])

    def _build_hop_heuristic(self, goal):
        """
        Admissible heuristic for abstract graphs (no lat/lon).

        Strategy: reverse-BFS from goal to count the minimum number of hops
        each node needs to reach the goal, then multiply by the cheapest edge
        cost in the graph.  This never overestimates the true cost, so A*
        remains optimal while Greedy gets real directional guidance.

        Result cached per goal node so it is computed at most once per search.
        """
        from collections import deque

        # Cheapest single edge cost (lower bound per hop)
        min_cost = min(
            (w for neighbors in self.edges.values() for _, w in neighbors),
            default=1.0
        )

        # Reverse adjacency: pred[v] = list of nodes u with edge u→v
        reverse = {}
        for u in self.edges:
            for v, _ in self.edges[u]:
                reverse.setdefault(v, []).append(u)

        # BFS backward from goal
        hops = {goal: 0}
        q = deque([goal])
        while q:
            node = q.popleft()
            for pred in reverse.get(node, []):
                if pred not in hops:
                    hops[pred] = hops[node] + 1
                    q.append(pred)

        self._h_goal  = goal
        self._h_cache = {n: hops.get(n, 0) * min_cost for n in self.nodes}

    def heuristic(self, a, b):
        """
        Geographic heuristic (km) when lat/lon are available.
        For abstract graphs: hop-based admissible heuristic
        (hop_count × min_edge_cost), auto-computed and cached per goal.
        """
        la = self.nodes[a]['lat']
        lb = self.nodes[b]['lat']
        if la is None or lb is None:
            if getattr(self, '_h_goal', None) != b:
                self._build_hop_heuristic(b)
            return self._h_cache.get(a, 0.0)
        lat1 = math.radians(la);  lon1 = math.radians(self.nodes[a]['lon'])
        lat2 = math.radians(lb);  lon2 = math.radians(self.nodes[b]['lon'])
        R = 6371.0
        dlat = (lat2 - lat1) * R
        dlon = (lon2 - lon1) * R * math.cos((lat1 + lat2) / 2)
        return math.sqrt(dlat**2 + dlon**2)

    @property
    def num_nodes(self):
        return len(self.nodes)

    @property
    def num_edges(self):
        total = sum(len(v) for v in self.edges.values())
        return total if self.directed else total // 2


def create_curitiba_graph():
    """
    Logistics network: Curitiba metropolitan region (Paraná, Brazil).
    Nodes = city hubs / distribution centers.
    Edge weights = approximate road distances (km).
    """
    g = Graph()

    g.add_node('CWB', 'Curitiba',              -25.4284, -49.2733)
    g.add_node('SJP', 'São José dos Pinhais',  -25.5350, -49.2113)
    g.add_node('PIN', 'Pinhais',               -25.4427, -49.1930)
    g.add_node('COL', 'Colombo',               -25.2927, -49.2238)
    g.add_node('ALT', 'Almirante Tamandaré',   -25.3219, -49.3234)
    g.add_node('CLA', 'Campo Largo',           -25.4587, -49.5294)
    g.add_node('ARA', 'Araucária',             -25.5927, -49.4126)
    g.add_node('FRG', 'Fazenda Rio Grande',    -25.6600, -49.3100)
    g.add_node('MAN', 'Mandirituba',           -25.7700, -49.3300)
    g.add_node('CON', 'Contenda',              -25.6790, -49.5370)
    g.add_node('BAN', 'Balsa Nova',            -25.5760, -49.6270)
    g.add_node('LAP', 'Lapa',                  -25.7672, -49.7157)

    g.add_edge('CWB', 'SJP', 15)
    g.add_edge('CWB', 'PIN', 12)
    g.add_edge('CWB', 'COL', 20)
    g.add_edge('CWB', 'ALT', 22)
    g.add_edge('CWB', 'CLA', 35)
    g.add_edge('CWB', 'ARA', 37)
    g.add_edge('PIN', 'SJP', 10)
    g.add_edge('PIN', 'COL', 18)
    g.add_edge('COL', 'ALT', 16)
    g.add_edge('ALT', 'CLA', 25)
    g.add_edge('CLA', 'ARA', 30)
    g.add_edge('CLA', 'BAN', 20)
    g.add_edge('ARA', 'FRG', 18)
    g.add_edge('ARA', 'CON', 28)
    g.add_edge('FRG', 'MAN', 22)
    g.add_edge('FRG', 'SJP', 15)
    g.add_edge('MAN', 'CON', 18)
    g.add_edge('CON', 'BAN', 22)
    g.add_edge('BAN', 'LAP', 35)

    return g
