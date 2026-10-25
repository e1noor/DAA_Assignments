import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from algorithms import kruskal, prim


def graph(n, m, seed):
    rng = random.Random(seed)
    edges = [[i - 1, i, rng.randint(-10**9, 10**9)] for i in range(1, n)]
    while len(edges) < m:
        edges.append([rng.randrange(n), rng.randrange(n), rng.randint(-10**9, 10**9)])
    return edges


def main():
    report = {'python': sys.version, 'platform': platform.platform(),
              'processor': platform.processor(), 'timer': 'time.perf_counter_ns',
              'warmup': 'one complete untimed call per method per size',
              'boundary': 'algorithm call, including its data structures; no input generation, JSON I/O or compilation',
              'repetitions': 5, 'rows': []}
    for n, m in [(1000, 2500), (10000, 25000), (100000, 250000)]:
        seed = 20261025 + n
        edges = graph(n, m, seed)
        samples = {method.__name__: [] for method in (kruskal, prim)}
        expected = kruskal(n, edges)['cost']
        for method in (kruskal, prim):
            assert method(n, edges)['cost'] == expected
        for repetition in range(5):
            methods = (kruskal, prim) if repetition % 2 == 0 else (prim, kruskal)
            for method in methods:
                start = time.perf_counter_ns()
                result = method(n, edges)
                elapsed = (time.perf_counter_ns() - start) / 1_000_000
                assert result['cost'] == expected
                samples[method.__name__].append(elapsed)
        report['rows'].append({'n': n, 'm': m, 'seed': seed, 'samples_ms': samples,
                              'median_ms': {name: statistics.median(values) for name, values in samples.items()}})
    (ROOT / 'tests/benchmark.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
