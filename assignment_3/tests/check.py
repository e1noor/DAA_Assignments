"""Independent oracles, witness checks, limits, and a real mixed JSONL process."""
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from algorithms import dag, dsu, kruskal, prim, reconstruct_route, scc, topo


def reachability(n, edges):
    reach = [[u == v for v in range(n)] for u in range(n)]
    for u, v, *_ in edges:
        reach[u][v] = True
    for k in range(n):
        for u in range(n):
            for v in range(n):
                reach[u][v] |= reach[u][k] and reach[k][v]
    return reach


def forest_valid(n, edges, result):
    ids = result['edge_ids']
    if len(set(ids)) != len(ids) or any(not 0 <= i < len(edges) for i in ids):
        return False
    groups = [{v} for v in range(n)]
    cost = 0
    for i in ids:
        u, v, w = edges[i]
        a = next(g for g in groups if u in g)
        b = next(g for g in groups if v in g)
        if a is b:
            return False
        groups.remove(b)
        a.update(b)
        cost += w
    return (cost == result['cost'] and len(groups) == result['components']
            and all(any(u in g and v in g for g in groups) for u, v, _ in edges))


def exhaustive_cost(n, edges):
    best = None
    # A spanning forest has a fixed size, determined independently by reachability.
    undirected = [(u, v) for u, v, _ in edges] + [(v, u) for u, v, _ in edges]
    r = reachability(n, undirected)
    c = sum(not any(r[u][v] for v in range(u)) for u in range(n))
    for ids in itertools.combinations(range(len(edges)), n - c):
        candidate = {'edge_ids': list(ids), 'cost': sum(edges[i][2] for i in ids), 'components': c}
        if forest_valid(n, edges, candidate):
            best = candidate['cost'] if best is None else min(best, candidate['cost'])
    return best


def small_random():
    rng = random.Random(20261025)
    for _ in range(150):
        n = rng.randrange(1, 7)
        edges = [[rng.randrange(n), rng.randrange(n), rng.randrange(-5, 6)] for _ in range(rng.randrange(9))]
        optimum = exhaustive_cost(n, edges)
        for method in (kruskal, prim):
            result = method(n, edges)
            assert forest_valid(n, edges, result) and result['cost'] == optimum
        directed = [e[:2] for e in edges]
        reach = reachability(n, directed)
        result = scc(n, directed)
        labels = result['component']
        assert all((labels[u] == labels[v]) == (reach[u][v] and reach[v][u])
                   for u in range(n) for v in range(n))
        assert {tuple(p) for p in result['condensation']} == {
            (labels[u], labels[v]) for u, v in directed if labels[u] != labels[v]}
        assert len(result['condensation']) == len({tuple(p) for p in result['condensation']})
        # Kahn's algorithm is an independent cycle oracle, not the tested DFS.
        indegree = [0] * n
        for u, v in directed:
            indegree[v] += 1
        queue = [u for u in range(n) if indegree[u] == 0]
        for u in queue:
            for a, v in directed:
                if a == u:
                    indegree[v] -= 1
                    if indegree[v] == 0:
                        queue.append(v)
        acyclic = len(queue) == n
        t = topo(n, directed)
        assert t['acyclic'] == acyclic
        if acyclic:
            positions = {u: i for i, u in enumerate(t['order'])}
            assert len(positions) == n and all(positions[u] < positions[v] for u, v in directed)
        else:
            assert t['order'] == []
        source = rng.randrange(n)
        d = dag(n, edges, source)
        assert d['acyclic'] == acyclic
        if not acyclic:
            assert d['distance'] == d['parent_edge'] == []
            continue
        # Bellman-Ford relaxation is independent of DFS/topological order.
        distance = [None] * n
        distance[source] = 0
        for _ in range(n - 1):
            for u, v, w in edges:
                if distance[u] is not None and (distance[v] is None or distance[u] + w < distance[v]):
                    distance[v] = distance[u] + w
        assert d['distance'] == distance
        for target in range(n):
            route = reconstruct_route(edges, source, target, d)
            if distance[target] is None:
                assert route is None and d['parent_edge'][target] == -1
            else:
                assert sum(edges[i][2] for i in route) == distance[target]


def route_examples():
    edges = [[0, 1, 2], [0, 1, 2], [1, 2, -3], [0, 2, -1]]
    result = dag(4, edges, 0)
    routes = {str(v): reconstruct_route(edges, 0, v, result) for v in range(4)}
    assert routes == {'0': [], '1': [0], '2': [3], '3': None}
    alternate = dict(result, parent_edge=[-1, 1, 2, -1])
    assert reconstruct_route(edges, 0, 2, alternate) == [1, 2]
    invalid = dict(result, parent_edge=[-1, 2, 2, -1])
    try:
        reconstruct_route(edges, 0, 1, invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid witness accepted')
    triangle = [[0, 1, 1], [1, 2, 1], [0, 2, 1]]
    assert forest_valid(3, triangle, {'cost': 2, 'edge_ids': [1, 2], 'components': 1})
    assert not forest_valid(3, triangle, {'cost': 3, 'edge_ids': [0, 1, 2], 'components': 1})
    return {'edges': edges, 'result': result, 'routes': routes,
            'alternative_route': [1, 2], 'invalid_witness_rejected': True}


def boundaries_and_limits():
    for method in (kruskal, prim):
        assert method(0, []) == {'cost': 0, 'edge_ids': [], 'components': 0}
        assert method(3, [[0, 0, -10**9]])['components'] == 3
    assert dsu(0, []) == {'states': []}
    assert scc(0, []) == {'component': [], 'condensation': []}
    assert topo(0, []) == {'acyclic': True, 'order': []}
    assert dag(1, [], 0) == {'acyclic': True, 'distance': [0], 'parent_edge': [-1]}
    assert not dag(3, [[1, 2, 0], [2, 1, 0]], 0)['acyclic']
    n, m = 100000, 250000
    for method in (kruskal, prim):
        assert method(n, []) == {'cost': 0, 'edge_ids': [], 'components': n}
    assert len(set(scc(n, [])['component'])) == n
    assert len(topo(n, [])['order']) == n
    assert dag(n, [], n - 1)['distance'] == [None] * (n - 1) + [0]
    chain = [[u, u + 1] for u in range(n - 1)]
    directed = chain + [[0, n - 1]] * (m - len(chain))
    assert topo(n, directed)['order'] == list(range(n))
    labels = scc(n, directed)['component']
    assert len(set(labels)) == n
    assert len(set(scc(n, chain + [[n - 1, 0]])['component'])) == 1
    assert not topo(n, chain + [[n - 1, 0]])['acyclic']
    weighted = [[u, v, -10**9] for u, v in directed]
    result = dag(n, weighted, 0)
    assert result['distance'][-1] == -(n - 1) * 10**9
    assert len(reconstruct_route(weighted, 0, n - 1, result)) == n - 1
    for method in (kruskal, prim):
        result = method(n, weighted)
        assert result['cost'] == -(n - 1) * 10**9 and result['components'] == 1
        assert len(set(result['edge_ids'])) == n - 1
    positive = [[u, v, 10**9] for u, v in chain]
    assert dag(n, positive, 0)['distance'][-1] == (n - 1) * 10**9
    operations = chain + [[0, n - 1]] * (m - len(chain))
    assert dsu(n, operations)['states'][-1] == [1, n]
    # Independent small DSU oracle: explicit sets, no parent tree.
    rng = random.Random(59)
    operations = [[rng.randrange(20), rng.randrange(20)] for _ in range(100)]
    groups, expected = [{u} for u in range(20)], []
    for u, v in operations:
        a, b = next(g for g in groups if u in g), next(g for g in groups if v in g)
        if a is not b:
            groups.remove(b)
            a.update(b)
        expected.append([len(groups), max(map(len, groups))])
    assert dsu(20, operations)['states'] == expected


def mixed_process():
    requests = [json.loads(s) for s in (ROOT / 'tests/inputs.jsonl').read_text().splitlines()]
    expected = [json.loads(s) for s in (ROOT / 'tests/expected.jsonl').read_text().splitlines()]
    completed = subprocess.run([sys.executable, str(ROOT / 'src/main.py')],
        input='\n'.join(json.dumps(r) for r in requests * 40) + '\n',
        text=True, capture_output=True, check=True)
    actual = [json.loads(line) for line in completed.stdout.splitlines()]
    assert not completed.stderr and actual == expected * 40
    (ROOT / 'tests/actual.jsonl').write_text('\n'.join(json.dumps(a) for a in actual[:len(requests)]) + '\n')
    return len(actual)


if __name__ == '__main__':
    small_random()
    routes = route_examples()
    boundaries_and_limits()
    count = mixed_process()
    summary = {'status': 'PASS', 'random_graphs': 150, 'seed': 20261025,
               'max_n': 100000, 'max_m': 250000, 'mixed_requests': count,
               'routes': routes}
    (ROOT / 'tests/results.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
