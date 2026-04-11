import networkx as nx
import time
from heapq import heappush, heappop
import ast
import os

G = nx.DiGraph()

with open(os.path.join(os.path.dirname(__file__), "congress.edgelist")) as f:
    for line in f:
        parts = line.strip().split(maxsplit=2)

        if len(parts) < 3:
            continue

        u = int(parts[0])
        v = int(parts[1])

        # converter {'weight': x}
        data = ast.literal_eval(parts[2])
        weight = data.get("weight", 1)

        G.add_edge(u, v, weight=weight)
# =========================
# escolher origem/destino
# =========================
source = 0
target = list(G.nodes())[50]

print(f"\nOrigem: {source} | Destino: {target}\n")

# =========================
# heurística (simples)
# =========================
def heuristic(u, v):
    return abs(u - v)  # simples (pode melhorar)

# =========================
# GREEDY (Best-First Search)
# =========================
def greedy_search(G, start, goal):
    visited = set()
    pq = []
    heappush(pq, (0, start, [start]))

    while pq:
        _, node, path = heappop(pq)

        if node == goal:
            return path

        if node in visited:
            continue

        visited.add(node)

        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                h = heuristic(neighbor, goal)
                heappush(pq, (h, neighbor, path + [neighbor]))

    return []

# =========================
# DIJKSTRA
# =========================
start = time.time()
path_dijkstra = nx.dijkstra_path(G, source, target, weight="weight")
time_dijkstra = time.time() - start

# =========================
# A*
# =========================
start = time.time()
path_astar = nx.astar_path(G, source, target, heuristic=heuristic, weight="weight")
time_astar = time.time() - start

# =========================
# GREEDY
# =========================
start = time.time()
path_greedy = greedy_search(G, source, target)
time_greedy = time.time() - start

# =========================
# BFS
# =========================
start = time.time()
path_bfs = nx.shortest_path(G, source, target)
time_bfs = time.time() - start

# =========================
# DFS
# =========================
start = time.time()
dfs_tree = nx.dfs_tree(G, source)

try:
    path_dfs = nx.shortest_path(dfs_tree, source, target)
except:
    path_dfs = []

time_dfs = time.time() - start

# =========================
# custo do caminho
# =========================
def path_cost(G, path):
    cost = 0
    for u, v in zip(path[:-1], path[1:]):
        cost += G[u][v]["weight"]
    return cost

# =========================
# print resultados
# =========================
def print_result(name, path, t):
    if path:
        cost = path_cost(G, path)
        print(f"{name}:")
        print(f"  Nós: {len(path)}")
        print(f"  Arestas: {len(path)-1}")
        print(f"  Custo: {cost:.6f}")
        print(f"  Tempo: {t:.6f}s\n")
    else:
        print(f"{name}: sem caminho\n")

print_result("Dijkstra", path_dijkstra, time_dijkstra)
print_result("A*", path_astar, time_astar)
print_result("Greedy", path_greedy, time_greedy)
print_result("BFS", path_bfs, time_bfs)
print_result("DFS", path_dfs, time_dfs)