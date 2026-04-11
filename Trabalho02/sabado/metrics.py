"""
Performance metrics collection.
Uses time.perf_counter() for wall-clock time and tracemalloc for peak memory.
Each call to measure_algorithm() runs the algorithm `runs` times and returns
mean ± std for: execution time (ms), peak memory (KB), nodes expanded.
"""

import time
import tracemalloc
import statistics


def _run_once(func, graph, start, goal):
    """Execute func once and return (path, cost, nodes_expanded, time_ms, peak_kb)."""
    tracemalloc.start()
    t0 = time.perf_counter()

    path, cost, nodes_expanded = func(graph, start, goal)

    elapsed = (time.perf_counter() - t0) * 1000   # ms
    _, peak = tracemalloc.get_traced_memory()       # bytes
    tracemalloc.stop()

    return path, cost, nodes_expanded, elapsed, peak / 1024


def measure_algorithm(func, graph, start, goal, runs=5):
    """
    Run `func` `runs` times and aggregate metrics.

    Returns dict:
      path, cost                  — result from last run
      nodes_expanded_mean/std     — float
      time_mean_ms / time_std_ms  — float
      memory_mean_kb / memory_std_kb — float
      runs                        — int
    """
    times, mems, nodes_list = [], [], []
    last_path, last_cost = None, float('inf')

    for _ in range(runs):
        path, cost, nodes, t, mem = _run_once(func, graph, start, goal)
        times.append(t)
        mems.append(mem)
        nodes_list.append(nodes)
        last_path, last_cost = path, cost

    def _std(data):
        return statistics.stdev(data) if len(data) > 1 else 0.0

    return {
        'path':                  last_path,
        'cost':                  last_cost,
        'nodes_expanded_mean':   statistics.mean(nodes_list),
        'nodes_expanded_std':    _std(nodes_list),
        'time_mean_ms':          statistics.mean(times),
        'time_std_ms':           _std(times),
        'memory_mean_kb':        statistics.mean(mems),
        'memory_std_kb':         _std(mems),
        'runs':                  runs,
    }
