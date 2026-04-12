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
    Algoritmo de Dijkstra (Sem bibliotecas externas).
    Prioridade: g(n) = custo acumulado do início até n.
    Expande na ordem do menor custo acumulado; garante o caminho ótimo.
    """
    # A "fronteira" guarda os caminhos a serem explorados.
    # Formato: (custo_g, no_atual, caminho_ate_aqui)
    # Não precisamos do tie_break (_ctr) aqui, pois a busca manual resolve isso.
    frontier = [(0, start, [start])]
    
    # Dicionário de nós fechados/visitados: no -> melhor custo g visto
    closed = {} 

    while frontier:
        # --- Simulando o heapq.heappop(heap) sem bibliotecas ---
        # Busca o nó com o menor custo g na lista da fronteira
        min_index = 0
        for i in range(1, len(frontier)):
            if frontier[i][0] < frontier[min_index][0]:
                min_index = i
        
        # Remove e pega os dados do caminho mais promissor
        g, node, path = frontier.pop(min_index)
        # -------------------------------------------------------

        # Se já expandimos este nó com um custo igual ou menor, ignoramos
        if node in closed:
            continue
            
        # Marca o nó como fechado/expandido com seu custo mínimo
        closed[node] = g

        # Se chegamos ao objetivo, retornamos exatamente no seu formato
        if node == goal:
            return path, g, len(closed)

        # Expande os vizinhos usando o método da classe do grafo
        for nbr, w in graph.get_neighbors(node):
            if nbr not in closed:
                # Adiciona o novo caminho à fronteira
                frontier.append((g + w, nbr, path + [nbr]))

    # Se a fronteira esvaziar e não acharmos o objetivo
    return None, float('inf'), len(closed)


# ──────────────────────────────────────────────────────────────────────────────
def greedy_best_first(graph, start, goal):
    """
    Algoritmo Greedy Best-First Search (Busca Gulosa) sem bibliotecas.
    Prioridade: f(n) = h(n).
    Ignora o custo real g(n) para tomada de decisão, usando apenas o "palpite" da heurística.
    Rápido, mas NÃO garante o caminho ótimo/mais curto.
    """
    # A fronteira guarda o (Custo Heurístico H, Custo Real G, nó, caminho)
    # Precisamos rastrear o 'g' apenas para saber o custo final do caminho ao terminar,
    # mas ele NÃO será usado para decidir qual caminho pegar.
    frontier = [(0, 0, start, [start])]

    # Conjunto de nós já visitados
    closed = set()

    while frontier:
        # --- Simulando a fila de prioridade ---
        # Busca o nó com o menor custo H (o que parece mais perto do fim)
        min_index = 0
        for i in range(1, len(frontier)):
            if frontier[i][0] < frontier[min_index][0]:
                min_index = i
        
        # Remove e desempacota o caminho
        h, g, node, path = frontier.pop(min_index)
        # --------------------------------------

        # Se já fechamos este nó, ignoramos (evita loops)
        if node in closed:
            continue
            
        # Marca o nó como visitado
        closed.add(node)

        # Se chegamos ao objetivo, retornamos (o 'g' rastreado nos diz quanto custou)
        if node == goal:
            return path, g, len(closed)

        # Expande os vizinhos
        for nbr, w in graph.get_neighbors(node):
            if nbr not in closed:
                novo_g = g + w  # Acumula o custo real para estatística final

                # Adiciona à fronteira ordenando EXCLUSIVAMENTE pelo palpite (h=0)
                frontier.append((0, novo_g, nbr, path + [nbr]))

    # Se a fronteira esvaziar e não acharmos o objetivo
    return None, float('inf'), len(closed)

# ──────────────────────────────────────────────────────────────────────────────
def a_star(graph, start, goal):
    """
    Algoritmo A* (A-Star) sem bibliotecas.
    Prioridade: f(n) = g(n) + h(n).
    g(n) = custo exato acumulado da origem até n.
    h(n) = estimativa heurística de n até o objetivo.
    """
    # A fronteira agora guarda o custo F, o custo G, o nó e o caminho.
    # f_inicial = g(0) + h(start) = 0 + 0
    frontier = [(0, 0, start, [start])]
    
    # Dicionário de nós fechados: no -> melhor custo G visto
    # (No A*, guardamos o G, não o F, para saber se achamos um atalho real para um nó já visto)
    closed = {} 

    while frontier:
        # --- Simulando a fila de prioridade ---
        # Busca o nó com o menor custo F (f = g + h)
        min_index = 0
        for i in range(1, len(frontier)):
            if frontier[i][0] < frontier[min_index][0]:
                min_index = i
        
        # Remove e desempacota o caminho mais promissor
        f, g, node, path = frontier.pop(min_index)
        # --------------------------------------

        # Se já fechamos este nó com um custo G menor ou igual, ignoramos
        if node in closed and closed[node] <= g:
            continue
            
        # Marca o nó como fechado com seu custo G mínimo
        closed[node] = g

        # Se chegamos ao objetivo, retornamos (o G será o custo total exato)
        if node == goal:
            return path, g, len(closed)

        # Expande os vizinhos
        for nbr, w in graph.get_neighbors(node):
            novo_g = g + w
            
            # Só exploramos o vizinho se nunca o vimos, ou se achamos um caminho MAIS BARATO até ele
            if nbr not in closed or novo_g < closed[nbr]:
                frontier.append((novo_g, novo_g, nbr, path + [nbr]))

    # Se a fronteira esvaziar e não acharmos o objetivo
    return None, float('inf'), len(closed)

# ──────────────────────────────────────────────────────────────────────────────
def dfs(graph, start, goal):
    """
    Algoritmo de Busca em Profundidade (DFS) sem bibliotecas.
    Usa uma Pilha (Stack) para explorar o grafo o mais fundo possível antes de retroceder.
    Aviso: O DFS encontra *um* caminho, mas NÃO garante que seja o caminho mais curto/barato.
    """
    # A "pilha" guarda os caminhos a serem explorados.
    # Formato: (custo_g, no_atual, caminho_ate_aqui)
    stack = [(0, start, [start])]
    
    # Conjunto de nós já visitados para evitar loops infinitos
    closed = set() 

    while stack:
        # Tira o ÚLTIMO elemento adicionado na lista (comportamento de Pilha/Stack)
        # Isso é O(1) e muito mais rápido que a busca do Dijkstra!
        g, node, path = stack.pop()

        # Se já visitamos este nó, ignoramos para não andar em círculos
        if node in closed:
            continue
            
        # Marca o nó como visitado
        closed.add(node)

        # Se chegamos ao objetivo, retornamos
        if node == goal:
            return path, g, len(closed)

        # Expande os vizinhos
        for nbr, w in graph.get_neighbors(node):
            # Só adicionamos à pilha se o vizinho ainda não foi explorado
            if nbr not in closed:
                # Adiciona o novo caminho no topo da pilha
                stack.append((g + w, nbr, path + [nbr]))

    # Se a pilha esvaziar e não acharmos o objetivo
    return None, float('inf'), len(closed)

# ──────────────────────────────────────────────────────────────────────────────
def bfs(graph, start, goal):
    """
    Algoritmo de Busca em Largura (BFS) sem bibliotecas.
    Usa uma Fila (Queue) para explorar o grafo em camadas (nível por nível).
    Garante o caminho com o menor número de nós, mas ignora o peso das arestas.
    """
    # A "fila" guarda os caminhos a serem explorados.
    # Formato: (custo_g, no_atual, caminho_ate_aqui)
    queue = [(0, start, [start])]
    
    # Conjunto de nós já visitados para evitar loops
    closed = set() 

    while queue:
        # Tira o PRIMEIRO elemento adicionado na lista (comportamento de Fila/Queue)
        # Nota: .pop(0) em listas nativas do Python move todos os elementos, 
        # então é um pouco mais lento que um deque real, mas atende à regra "sem bibliotecas".
        g, node, path = queue.pop(0)

        # Se já visitamos este nó, ignoramos
        if node in closed:
            continue
            
        # Marca o nó como visitado
        closed.add(node)

        # Se chegamos ao objetivo, retornamos
        if node == goal:
            return path, g, len(closed)

        # Expande os vizinhos
        for nbr, w in graph.get_neighbors(node):
            # Só adicionamos à fila se o vizinho ainda não foi explorado
            if nbr not in closed:
                # Adiciona o novo caminho no FINAL da fila
                queue.append((g + w, nbr, path + [nbr]))

    # Se a fila esvaziar e não acharmos o objetivo
    return None, float('inf'), len(closed)