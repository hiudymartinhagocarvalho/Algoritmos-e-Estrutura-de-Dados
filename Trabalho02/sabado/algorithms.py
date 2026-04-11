"""
Search algorithm implementations — all coded from scratch (no external algo libraries).

Each function signature: algo(graph, start, goal) -> (path, cost, nodes_expanded)
  path          : list[str] from start to goal, or None if unreachable
  cost          : float total accumulated edge weight (inf if unreachable)
  nodes_expanded: int number of nodes popped from the frontier

Big-O (V = vertices, E = edges):
  Dijkstra       O((V+E) log V) time,  O(V) space  — optimal (min-cost path)
  Greedy BFS     O((V+E) log V) time,  O(V) space  — not optimal
  A*             O((V+E) log V) time,  O(V) space  — optimal with admissible h
  DFS            O(V+E) time,          O(V) space  — not optimal (weighted)
  BFS            O(V+E) time,          O(V) space  — optimal only for unweighted
"""

import heapq
from collections import deque


# ──────────────────────────────────────────────────────────────────────────────
def dijkstra(graph, start, goal):
    """
    Dijkstra's algorithm.
    Priority: g(n) = accumulated cost from start to n.
    Expands in order of lowest accumulated cost; guaranteed optimal.
    """
    _ctr = 0
    # heap entries: (g, tie_break, node, path)
    heap = [(0, _ctr, start, [start])]
    closed = {}   # node -> best g seen (once popped)

    while heap:
        g, _, node, path = heapq.heappop(heap)

        if node in closed:
            continue
        closed[node] = g

        if node == goal:
            return path, g, len(closed)

        for nbr, w in graph.get_neighbors(node):
            if nbr not in closed:
                _ctr += 1
                heapq.heappush(heap, (g + w, _ctr, nbr, path + [nbr]))

    return None, float('inf'), len(closed)


# ──────────────────────────────────────────────────────────────────────────────
def greedy_best_first(graph, start, goal):
    """
    Greedy Best-First Search.
    Priority: h(n) = straight-line distance to goal (heuristic only).
    Fast but suboptimal — ignores accumulated cost.
    """
    _ctr = 0
    h0 = graph.heuristic(start, goal)
    # heap entries: (h, tie_break, node, path, g)
    heap = [(h0, _ctr, start, [start], 0)]
    visited = set()
    expanded = 0

    while heap:
        h, _, node, path, g = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, g, expanded

        for nbr, w in graph.get_neighbors(node):
            if nbr not in visited:
                _ctr += 1
                heapq.heappush(heap, (graph.heuristic(nbr, goal), _ctr,
                                      nbr, path + [nbr], g + w))

    return None, float('inf'), expanded


# ──────────────────────────────────────────────────────────────────────────────
def a_star(graph, start, goal):
    """
    A* Search.
    Priority: f(n) = g(n) + h(n).
    Combines Dijkstra's cost-awareness with Greedy's directional bias.
    Optimal when h is admissible (Euclidean distance never overestimates road km).
    """
    _ctr = 0
    h0 = graph.heuristic(start, goal)
    # heap entries: (f, g, tie_break, node, path)
    heap = [(h0, 0, _ctr, start, [start])]
    best_g = {}   # node -> lowest g seen when expanded
    expanded = 0

    while heap:
        f, g, _, node, path = heapq.heappop(heap)

        if node in best_g and best_g[node] <= g:
            continue
        best_g[node] = g
        expanded += 1

        if node == goal:
            return path, g, expanded

        for nbr, w in graph.get_neighbors(node):
            g_new = g + w
            if nbr not in best_g or best_g[nbr] > g_new:
                h_new = graph.heuristic(nbr, goal)
                _ctr += 1
                heapq.heappush(heap, (g_new + h_new, g_new, _ctr, nbr, path + [nbr]))

    return None, float('inf'), expanded


# ──────────────────────────────────────────────────────────────────────────────
def dfs(graph, start, goal):
    """
    Depth-First Search (iterative).
    Explores deepest nodes first via LIFO stack.
    Does NOT guarantee optimal path on weighted graphs.
    """
    # stack entries: (node, path, g)
    stack = [(start, [start], 0)]
    visited = set()
    expanded = 0

    while stack:
        node, path, g = stack.pop()

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, g, expanded

        # push in reverse so first neighbor is explored first
        for nbr, w in reversed(graph.get_neighbors(node)):
            if nbr not in visited:
                stack.append((nbr, path + [nbr], g + w))

    return None, float('inf'), expanded


# ──────────────────────────────────────────────────────────────────────────────
def bfs(graph, start, goal):
    """
    Breadth-First Search.
    Explores level by level via FIFO queue.
    Optimal for unweighted graphs (min edges); NOT optimal for weighted graphs.
    """
    queue = deque([(start, [start], 0)])
    visited = set()
    expanded = 0

    while queue:
        node, path, g = queue.popleft()

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, g, expanded

        for nbr, w in graph.get_neighbors(node):
            if nbr not in visited:
                queue.append((nbr, path + [nbr], g + w))

    return None, float('inf'), expanded
