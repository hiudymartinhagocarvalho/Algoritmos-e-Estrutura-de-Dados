"""
Graph and Search Algorithms Analysis
PUCPR · Pós-Graduação em Informática Aplicada
Fundamentos de Algoritmos e Estrutura de Dados

Graph: US Congress Twitter Influence Network (full — 475 nodes)

5 origin–destination pairs × 5 algorithms × 5 repetitions.
Metrics: execution time (ms), peak memory (KB), nodes expanded.
After the experiments, matplotlib PNG images are generated for each algorithm
showing the path taken on the full Congress graph.
"""

import os

from graph_loaders  import (load_congress_full_graph, find_reachable_pairs)
from algorithms     import dijkstra, greedy_best_first, a_star, dfs, bfs
from metrics        import measure_algorithm
from visualization  import visualize_graph, visualize_path
from plot_paths     import generate_path_plots, find_target, find_source

# ── configuration ─────────────────────────────────────────────────────────────
RUNS = 5

ALGORITHMS = {
    'Dijkstra': dijkstra,
    'Greedy':   greedy_best_first,
    'A*':       a_star,
    'DFS':      dfs,
    'BFS':      bfs,
}

_HERE             = os.path.dirname(os.path.abspath(__file__))
DATA_DIR          = os.path.join(_HERE, '..', '..', 'projetos', 'Trabalho02')
CONGRESS_JSON     = os.path.join(DATA_DIR, 'congress_network_data.json')
CONGRESS_EDGELIST = os.path.join(DATA_DIR, 'congress.edgelist')

BIG_O = {
    'Dijkstra': ('O((V+E) log V)', 'O(V)', 'Yes'),
    'Greedy':   ('O((V+E) log V)', 'O(V)', 'No'),
    'A*':       ('O((V+E) log V)', 'O(V)', 'Yes (admissible h)'),
    'DFS':      ('O(V+E)',         'O(V)', 'No'),
    'BFS':      ('O(V+E)',         'O(V)', 'Only unweighted'),
}

SEP  = '=' * 100
SEP2 = '-' * 100


# ── helpers ───────────────────────────────────────────────────────────────────

def fmt_path(graph, path):
    if not path:
        return 'NOT FOUND'
    return ' → '.join(graph.nodes[n]['name'] for n in path)

def fmt_cost(c):
    return f"{c:.4f}" if c != float('inf') else '∞'


# ── experiment runner ─────────────────────────────────────────────────────────

def run_for_graph(graph, graph_label, test_cases):
    results = {}

    print(f"\n\n{'#' * 100}")
    print(f"  GRAPH: {graph_label}")
    print(f"  {'directed' if graph.directed else 'undirected'} | "
          f"{graph.num_nodes} nodes | {graph.num_edges} edges")
    print(f"{'#' * 100}")

    print("\nNodes (first 20):")
    for i, (nid, d) in enumerate(graph.nodes.items()):
        if i >= 20:
            print(f"  ... ({graph.num_nodes - 20} more)")
            break
        print(f"  {nid:>4}  {d['name']}")

    for start, goal in test_cases:
        pair       = f"{start}->{goal}"
        pair_label = (f"{graph.nodes[start]['name']} "
                      f"→ {graph.nodes[goal]['name']}")
        results[pair] = {'label': pair_label, 'algos': {}}

        print(f"\n{SEP}")
        print(f"  TEST CASE: {pair_label}")
        print(SEP)

        for algo_name, algo_func in ALGORITHMS.items():
            m = measure_algorithm(algo_func, graph, start, goal, runs=RUNS)
            results[pair]['algos'][algo_name] = m

            print(f"\n  [{algo_name}]")
            print(f"    Path         : {fmt_path(graph, m['path'])}")
            print(f"    Cost         : {fmt_cost(m['cost'])}")
            print(f"    Nodes exp.   : {m['nodes_expanded_mean']:.1f} ± {m['nodes_expanded_std']:.2f}")
            print(f"    Time (ms)    : {m['time_mean_ms']:.5f} ± {m['time_std_ms']:.5f}")
            print(f"    Memory (KB)  : {m['memory_mean_kb']:.5f} ± {m['memory_std_kb']:.5f}")

    return results


# ── summary / complexity tables ───────────────────────────────────────────────

def print_summary_table(graph_label, results):
    print(f"\n{SEP}")
    print(f"  SUMMARY — {graph_label}")
    print(SEP)

    for pair, data in results.items():
        print(f"\n  Pair: {data['label']}")
        hdr = (f"  {'Algorithm':<12} {'Cost':>12} {'Nodes µ':>9} {'Nodes σ':>9}"
               f"  {'Time µ(ms)':>12} {'Time σ(ms)':>12}"
               f"  {'Mem µ(KB)':>11} {'Mem σ(KB)':>11}")
        print(hdr)
        print(f"  {SEP2}")
        for algo in ALGORITHMS:
            m = data['algos'][algo]
            print(
                f"  {algo:<12}"
                f" {fmt_cost(m['cost']):>12}"
                f" {m['nodes_expanded_mean']:>9.1f}"
                f" {m['nodes_expanded_std']:>9.2f}"
                f"  {m['time_mean_ms']:>12.5f}"
                f" {m['time_std_ms']:>12.5f}"
                f"  {m['memory_mean_kb']:>11.5f}"
                f" {m['memory_std_kb']:>11.5f}"
            )


def print_complexity_table():
    print(f"\n{SEP}")
    print("  ASYMPTOTIC COMPLEXITY")
    print(SEP)
    print(f"  {'Algorithm':<12} {'Time Complexity':>18} {'Space':>8}  {'Optimal?':<25}")
    print(f"  {SEP2}")
    for algo, (tc, sc, opt) in BIG_O.items():
        print(f"  {algo:<12} {tc:>18} {sc:>8}  {opt:<25}")


# ── Pyvis HTML visualizations ─────────────────────────────────────────────────

def generate_html_visualizations(graph, test_cases, prefix):
    out = f"output/{prefix}"
    os.makedirs(out, exist_ok=True)
    visualize_graph(graph, f"{out}/graph.html")
    start, goal = test_cases[0]
    for algo_name, algo_func in ALGORITHMS.items():
        path, _, _ = algo_func(graph, start, goal)
        safe = algo_name.lower().replace('*', 'star').replace(' ', '_')
        visualize_path(graph, path, algo_name,
                       f"{out}/path_{start}_{goal}_{safe}.html")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    print(SEP)
    print("  Graph and Search Algorithms Analysis")
    print("  PUCPR · Fundamentos de Algoritmos e Estrutura de Dados")
    print(f"  Repetitions per experiment: {RUNS}")
    print(SEP)

    # ── Primary: Congress Twitter (full graph) ────────────────────────────────
    print("\nLoading Congress Twitter Influence Network (full)...")
    g_congress = load_congress_full_graph(CONGRESS_JSON, CONGRESS_EDGELIST)
    print(f"  {g_congress.num_nodes} nodes, {g_congress.num_edges} edges")

    target = find_target(g_congress)
    source = find_source(g_congress, target)
    print(f"  Target (red)   : {g_congress.nodes[target]['name']}")
    print(f"  Source (yellow): {g_congress.nodes[source]['name']}")

    t_congress = find_reachable_pairs(g_congress, n_pairs=5)
    r_congress = run_for_graph(g_congress,
                               'US Congress Twitter Influence Network',
                               t_congress)
    print_summary_table('US Congress Twitter Influence Network', r_congress)

    # Pyvis HTMLs (first test pair)
    generate_html_visualizations(g_congress, t_congress, 'congress')

    # Matplotlib PNGs — paths to the red node (target)
    print(f"\n{SEP}")
    print("  GENERATING PATH IMAGES (matplotlib)")
    print(SEP)
    plot_results = {}
    for algo_name, algo_func in ALGORITHMS.items():
        path, cost, expanded = algo_func(g_congress, source, target)
        plot_results[algo_name] = {'path': path, 'cost': cost, 'expanded': expanded}
        path_str = fmt_path(g_congress, path)
        print(f"  {algo_name:<10} cost={cost:>10.2f}  expanded={expanded:>4}  "
              f"{path_str[:70]}{'...' if len(path_str) > 70 else ''}")

    generate_path_plots(g_congress, source, target, plot_results,
                        out_dir='output/congress')

    print_complexity_table()

    print(f"\n{SEP}")
    print("  Completed.")
    print("  HTML files : output/congress/")
    print("  PNG images : output/congress/congress_*.png")
    print(SEP)


if __name__ == '__main__':
    main()
