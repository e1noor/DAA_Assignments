from heapq import heappop, heappush


class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.largest = int(n > 0)

    def find(self, u):
        while u != self.parent[u]:
            self.parent[u] = self.parent[self.parent[u]]
            u = self.parent[u]
        return u

    def union(self, u, v):
        u, v = self.find(u), self.find(v)
        if u == v:
            return False
        if self.size[u] < self.size[v]:
            u, v = v, u
        self.parent[v] = u
        self.size[u] += self.size[v]
        self.components -= 1
        self.largest = max(self.largest, self.size[u])
        return True


def dsu(n, operations):
    sets = DisjointSet(n)
    states = []
    for u, v in operations:
        sets.union(u, v)
        states.append([sets.components, sets.largest])
    return {"states": states}


def kruskal(n, edges):
    sets = DisjointSet(n)
    selected, cost = [], 0
    for eid in sorted(range(len(edges)), key=lambda i: (edges[i][2], i)):
        u, v, w = edges[eid]
        if sets.union(u, v):
            selected.append(eid)
            cost += w
    return {"cost": cost, "edge_ids": selected, "components": sets.components}


def prim(n, edges):
    adjacency = [[] for _ in range(n)]
    for eid, (u, v, w) in enumerate(edges):
        adjacency[u].append((w, eid, v))
        adjacency[v].append((w, eid, u))
    visited = bytearray(n)
    selected, cost, components = [], 0, 0
    for root in range(n):
        if visited[root]:
            continue
        components += 1
        visited[root] = 1
        heap = []
        for entry in adjacency[root]:
            if not visited[entry[2]]:
                heappush(heap, entry)
        while heap:
            w, eid, v = heappop(heap)
            if visited[v]:
                continue
            visited[v] = 1
            selected.append(eid)
            cost += w
            for entry in adjacency[v]:
                if not visited[entry[2]]:
                    heappush(heap, entry)
    return {"cost": cost, "edge_ids": selected, "components": components}


def _finish_order(adjacency, detect_cycle=False):
    """Explicit DFS frames retain the next neighbor index, as recursive DFS does."""
    color = bytearray(len(adjacency))
    finished = []
    for root in range(len(adjacency)):
        if color[root]:
            continue
        color[root] = 1
        stack = [(root, 0)]
        while stack:
            u, index = stack[-1]
            if index == len(adjacency[u]):
                stack.pop()
                color[u] = 2
                finished.append(u)
                continue
            v = adjacency[u][index]
            stack[-1] = (u, index + 1)
            if color[v] == 0:
                color[v] = 1
                stack.append((v, 0))
            elif detect_cycle and color[v] == 1:
                return None
    return finished


def scc(n, edges):
    adjacency, transpose = [[] for _ in range(n)], [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        transpose[v].append(u)
    order = _finish_order(adjacency)
    component = [-1] * n
    label = 0
    for root in reversed(order):
        if component[root] != -1:
            continue
        component[root] = label
        stack = [root]
        while stack:
            u = stack.pop()
            for v in transpose[u]:
                if component[v] == -1:
                    component[v] = label
                    stack.append(v)
        label += 1
    pairs = {(component[u], component[v]) for u, v in edges
             if component[u] != component[v]}
    return {"component": component, "condensation": [list(p) for p in pairs]}


def topo(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
    order = _finish_order(adjacency, detect_cycle=True)
    if order is None:
        return {"acyclic": False, "order": []}
    return {"acyclic": True, "order": order[::-1]}


def dag(n, edges, source):
    adjacency = [[] for _ in range(n)]
    weighted = [[] for _ in range(n)]
    for eid, (u, v, w) in enumerate(edges):
        adjacency[u].append(v)
        weighted[u].append((v, w, eid))
    order = _finish_order(adjacency, detect_cycle=True)
    if order is None:
        return {"acyclic": False, "distance": [], "parent_edge": []}
    distance, parent = [None] * n, [-1] * n
    distance[source] = 0
    for u in reversed(order):
        if distance[u] is None:
            continue
        for v, w, eid in weighted[u]:
            candidate = distance[u] + w
            if distance[v] is None or candidate < distance[v]:
                distance[v] = candidate
                parent[v] = eid
    return {"acyclic": True, "distance": distance, "parent_edge": parent}


def reconstruct_route(edges, source, target, result):
    """Return original edge IDs; source -> []; unreachable/cyclic -> None.

    Reject malformed witnesses rather than looping indefinitely.
    """
    if not result["acyclic"]:
        return None
    distance, parent = result["distance"], result["parent_edge"]
    if not (0 <= source < len(distance) and 0 <= target < len(distance)):
        raise ValueError("vertex out of range")
    if distance[target] is None:
        return None
    route, seen = [], set()
    v = target
    while v != source:
        if v in seen:
            raise ValueError("cyclic parent witness")
        seen.add(v)
        eid = parent[v]
        if not 0 <= eid < len(edges):
            raise ValueError("invalid parent edge")
        u, endpoint, w = edges[eid]
        if endpoint != v or distance[u] is None or distance[u] + w != distance[v]:
            raise ValueError("inconsistent parent witness")
        route.append(eid)
        v = u
    return route[::-1]
