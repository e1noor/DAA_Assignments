"""UTF-8 JSON Lines adapter. No diagnostics are written to stdout."""
import json
import sys

from algorithms import dag, dsu, kruskal, prim, scc, topo


def dispatch(request):
    task = request["task"]
    if task == "ping":
        return {"pong": True}
    n = request["n"]
    if task == "dsu":
        return dsu(n, request["operations"])
    if task == "dag":
        return dag(n, request["edges"], request["source"])
    methods = {"kruskal": kruskal, "prim": prim, "scc": scc, "topo": topo}
    return methods[task](n, request["edges"])


def main():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        if line.strip():
            result = dispatch(json.loads(line))
            print(json.dumps(result, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
