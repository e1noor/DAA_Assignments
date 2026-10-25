# Test evidence

Run `python tools/run.py --check` from `assignment_3/`. Inputs and justified
expected results are versioned; `actual.jsonl` and `results.json` record a real run.
These are custom tests. No instructor public-check results are claimed.

## Fixture expectations

| Line | Purpose | Expected justification |
|---|---|---|
| 1 | Ping | Local adapter returns `pong=true`; confirm official contract. |
| 2 | DSU repeat and loop | Only 0–1 and 1–2 merge; final two components, largest size 3. |
| 3 | Kruskal, loop, parallel, isolate | Ignore loop; choose IDs 3 and 2 for cost -2; vertex 3 stays isolated. |
| 4 | Prim same graph | IDs 2 then 3 give the same optimal cost and two components. |
| 5 | SCC, duplicate cross edge | 0 and 1 mutually reachable, 2 alone; exactly one condensation edge. |
| 6 | Topological chain | 0 precedes 1 precedes 2. |
| 7 | DAG ties and negative edge | Distances `[0,2,-1,null]`; either direct 0–2 or tied path 0–1–2 is valid. |
| 8 | Unreachable directed cycle | Whole graph is cyclic although source 0 is isolated; return empty arrays. |
| 9 | Topological self-loop | A loop is a directed cycle. |
| 10 | State reset | Fresh DSU of size two with a loop must still have two singleton components. |

`mixed_process()` repeats all ten requests forty times through a real child
process. It checks exactly 400 JSON responses, fresh state, empty stderr and
the expected values. Exact fixture witnesses are deterministic examples only;
randomized tests validate non-unique outputs semantically.

## Independent oracles and witness validation

Seed 20261025 generates 150 graphs, 1–6 vertices and 0–8 edges, with loops,
parallel edges, isolates and weights -5..5. Exhaustive enumeration finds the
true minimum forest cost, while an explicit-set validator checks selected
IDs, acyclicity, total weight, components and spanning of original components.
Floyd–Warshall reachability checks SCC equivalence and exact condensation pairs.
Kahn's algorithm checks DFS cycle decisions; topological witnesses are checked
edge by edge. Bellman–Ford checks DAG distances and route reconstruction
checks each finite target. DSU has a separate explicit-set oracle (seed 59).

An equal-weight triangle accepts alternative forest `[1,2]` and rejects the
cycle `[0,1,2]`. Route examples accept the tied parallel witness `[1,2]` and
reject a parent edge pointing to the wrong endpoint. See `results.json` for
reachable/source/unreachable calls and actual route output.

## Boundaries and limits

Empty DSU/MST/SCC/topological graphs; single-vertex DAG; loops; n=100000
isolates connected by no edges in the algorithms' initialization; explicit
deep chains; a chain closed into one SCC/cycle; a cycle unreachable from
source; n=100000, m=250000 directed and weighted requests; 250000 union
operations; both ±10^9 weights and totals beyond 32-bit range.
The full-size directed input is a chain plus repeated 0–99999 edges.
Expected topological order is increasing, every SCC is a singleton, and the
negative-weight DAG/forest total is -99999000000000.

## Benchmark

Run `python tools/benchmark.py`; actual samples, medians, seeds and environment
are in `benchmark.json`. Generation is deterministic and outside timing.
