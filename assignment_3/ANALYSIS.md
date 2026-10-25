# Graph algorithms: design, correctness and evidence

## Scope and reproducibility

This standalone Python 3.12+ implementation follows the supplied one-page
Assignment 3 PDF. Its full template could not be fetched, so the exact official
adapter, ping contract, manifest schema, 18-group rubric and 36 public cases
remain unverified. The local runner and GitHub workflow are labeled accordingly.
Integration into the official template is required before assessment submission.

Run from `assignment_3/`:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/benchmark.py
python src/main.py < tests/inputs.jsonl
```

No build or installation is needed. On the preparation computer, `python` was
not on PATH; the actual interpreter was `..\.venv\Scripts\python.exe`.
Tests ran on CPython 3.14.3, Windows 11, Intel64 Family 6 Model 186 Stepping 3.
Python 3.12 is specified in CI but has not been executed locally.

Throughout, n counts vertices, m counts edges, q counts union operations,
k counts distinct condensation edges, and alpha is the inverse Ackermann function.
Space bounds exclude the caller's input unless stated, and include returned arrays.

## DSU

Initialize every vertex as its own root with size one. Find walks parent links
using path halving, a form of path compression. Union first finds the two roots;
if distinct, attach the smaller root below the larger root, update the surviving
size, decrement the component count and update the maximum size. Record counts
after every operation, including redundant unions and loops.

Invariant: parent trees partition exactly the connectivity classes induced by
processed operations; root sizes count their members. Initially this holds for
singletons. Compression replaces a parent by an ancestor, so membership is
unchanged. A successful union combines exactly two classes and their sizes;
an unsuccessful one changes no class. Thus component and largest counters are
correct after each prefix. Empty input has zero components and largest zero
internally; no states are returned without operations.

Time O(n + q alpha(n)) amortized; memory O(n + q), including output states.

## Kruskal minimum spanning forest

Sort original IDs by (weight, ID). Process in that order and accept an edge
only when its endpoints have different DSU roots. Sum its weight using Python
integers; preserve its original input ID. Start with n components, so isolates
are included. Self-loops and later parallel edges joining an existing tree are
rejected automatically. Negative and equal weights require no special case.

Invariant: accepted edges form a forest extendible to an optimal spanning
forest. The next accepted edge is a lightest edge crossing a cut separating
two current trees. By the cut exchange argument it can replace a no-lighter
edge in an optimal extension. On termination no input edge connects separate
trees, so every original connected component is spanned. The exchange argument
proves minimum total cost independently in every component.

Time O(n + m log(m+1) + m alpha(n)); memory O(n + m) for DSU, sorted IDs and
result. The n initialization term matters for many isolates.

## Prim minimum spanning forest

Build undirected adjacency lists of (weight, original ID, neighbor). For each
unvisited vertex, start a new tree and increment components. Push incident
edges leading to unvisited vertices. Repeatedly pop the smallest heap entry;
skip stale entries whose destination is already visited. Otherwise accept it,
visit its destination, and expose that vertex's outgoing candidates. Restart
after the heap empties to cover disconnected components and isolated vertices.

Invariant: accepted edges are a tree on the visited vertices of the current
component. Every frontier edge is represented in the heap; stale entries can
only delay, never change, the smallest eligible frontier edge. By the cut
property each accepted edge is safe for some minimum spanning tree. Exhausting
the frontier completes that component. Restarts give an optimal forest and
count all components. Loops never enter the frontier. Equal/parallel edges
may give different valid witnesses, while negative weights remain ordered.

This is lazy edge-heap Prim: time O(n + m log(m+1)), space O(n+m), including
adjacency and a heap with up to O(m) candidates. It does not claim the tighter
indexed-vertex-heap O(m log n) bound for arbitrary multigraphs.

## Kosaraju strongly connected components

Build adjacency and its transpose. First perform DFS on the original graph,
recording each vertex only when its frame finishes. Process vertices in reverse
finishing order; each unassigned vertex starts a DFS on the transpose, assigning
one new label. Finally scan original edges and deduplicate all unequal-label
pairs in a set. Pair order and SCC label numbers have no semantic significance.

The condensation graph is acyclic: a cycle among distinct SCCs would make them
mutually reachable, contradicting maximality. For an edge between SCCs, the
source SCC's maximum finishing time exceeds the destination SCC's. Consequently,
the next unassigned SCC in decreasing finish order cannot reach another
unassigned SCC through transpose edges. The transpose DFS therefore finds
exactly that SCC. Inductively all labels describe exactly mutual reachability.
The final scan includes every cross-SCC edge and set deduplication removes only
duplicates, proving the condensation result.

Time O(n+m) expected with hash-set deduplication; memory O(n+m+k). The returned
condensation is unsorted to retain linear expected time. Empty graph returns
two empty lists; loops stay within a component; parallel arcs are deduplicated.

## Three-state DFS topological sort

Colors are white (unseen), gray (active) and black (finished). Each explicit
frame stores (vertex, next-neighbor-index). Discover a white neighbor by pushing
a new gray frame; finish a vertex only after all its neighbors were processed.
A gray neighbor is a back edge, so return false and an empty order immediately.
Otherwise reverse finishing order after traversing every DFS root.

Invariant: gray vertices are exactly the current DFS ancestor path. An edge to
gray closes a directed cycle, including a self-loop. Conversely, DFS of a
directed cycle must encounter a gray back edge. Without such an edge, every
u->v has v finish before u (either in u's exploration or already black), so
reversing finish times places u before v. This proves both cycle detection
and the returned order. Disconnected roots and empty graphs are supported.

Time O(n+m); space O(n+m), including adjacency, colors, frames and output.
The frame stack has at most n entries; no recursive call or recursion-limit
increase is needed, even on a 100000-vertex chain.

## DAG shortest paths

First run the same three-state DFS on the ENTIRE graph, even components
unreachable from source. On any cycle, return false with two empty arrays.
Otherwise initialize all distances to None, parents to -1 and source to zero.
Visit vertices in topological order, skip unreachable vertices, and relax each
outgoing edge. A strict improvement stores the original edge ID as parent.

Induction on topological position proves correctness: when u is processed,
every incoming predecessor has already been processed. Every source-to-u path
ends at such a predecessor, so relaxing their final distances has considered
every possible final edge; the minimum distance to u is therefore final.
Unreachable vertices receive no finite relaxation. Each selected parent realizes
the recorded distance. Parents always point backward in the topological order,
so they cannot form a cycle. Negative weights are safe because no vertex needs
revisiting. Strict comparisons keep any earlier tied witness. The source has
distance zero and parent -1; a reachable incoming path to source would imply
a directed cycle, already rejected. Python integers safely hold ±99999000000000.

Time O(n+m); space O(n+m). The two adjacency representations retain original
IDs and allow sharing the iterative DFS helper. A DAG has n>=1 per the PDF.
Valid contract inputs are assumed; malformed requests are not assigned an
invented JSON error protocol.

## Route reconstruction helper

`reconstruct_route(edges, source, target, result)` returns original edge IDs
in forward order, [] for source, and None for unreachable/cyclic results.
Follow parent IDs backward from target, checking endpoints and distance
equalities, then reverse. The seen set rejects malformed cyclic witnesses;
invalid parent IDs and inconsistent distances raise ValueError. For a valid
DAG result, each step moves backward topologically and must reach source.
Time and extra space are O(L) for L edges in the route, at most O(n).
The caller supplies the same source used to compute the result.

Executed examples (`tests/results.json`):

```python
edges = [[0,1,2], [0,1,2], [1,2,-3], [0,2,-1]]
r = dag(4, edges, 0)
reconstruct_route(edges, 0, 1, r)  # [0], reachable
reconstruct_route(edges, 0, 0, r)  # [], source
reconstruct_route(edges, 0, 3, r)  # None, unreachable
reconstruct_route(edges, 0, 2, r)  # [3], direct path tied with [0,2]
alternate = dict(r, parent_edge=[-1,1,2,-1])
reconstruct_route(edges, 0, 2, alternate)  # [1,2], tied parallel edge
invalid = dict(r, parent_edge=[-1,2,2,-1])
reconstruct_route(edges, 0, 1, invalid)  # ValueError: wrong endpoint
```

## State reset, testing and actual observations

No algorithm stores mutable global state. Every request constructs its own
arrays, DSU, heap and adjacency. The JSONL loop dispatches independently and
prints exactly one compact JSON value per nonblank input line. Diagnostics
from development tools are outside the adapter. See the scope note for ping.

The actual custom suite passed 150 seeded small random graphs checked with
independent exhaustive enumeration, reachability, Kahn and Bellman–Ford oracles;
400 repeated mixed process requests; explicit route alternatives and invalid
witnesses; and limits n=100000, m/q=250000. Both signs of 10^9, negative loops,
isolates, parallel edges, deep chains, a single huge SCC, and unreachable cycles
are covered. `tests/README.md` justifies each fixture; inputs, expected results,
actual results, and summary are committed as separate files. Non-unique random
outputs are checked by validity and optimality, not literal equality of IDs.
These results do not establish that the unavailable official public cases pass.

## Kruskal versus Prim measurements

Five timed complete calls per method per size, on exactly the same in-memory
edge list for both methods. `random.Random(seed)` first creates a spanning chain,
then uniformly chosen endpoint pairs (loops and parallel edges permitted), with
uniform integer weights in [-10^9,10^9]. Sizes/seeds are in the table below.
The timer is `time.perf_counter_ns`; generation, imports, assertions and JSON
serialization are outside timing. All algorithm allocations, adjacency building
and sorting are inside. Each method has one complete untimed warm-up per size;
execution order alternates each repetition. No compilation occurs. GC uses its
normal interpreter settings. Raw samples and environment are in `tests/benchmark.json`.

| n | m | Seed | Kruskal samples (ms) | Median | Prim samples (ms) | Median |
|---:|---:|---:|---|---:|---|---:|
| 1000 | 2500 | 20262025 | 1.5211, 1.6061, 1.5176, 1.5889, 1.5099 | 1.5211 | 1.7615, 1.9165, 1.8497, 1.9582, 1.8645 | 1.8645 |
| 10000 | 25000 | 20271025 | 21.1882, 21.9491, 20.8437, 21.1924, 20.4055 | 21.1882 | 26.2070, 28.3278, 28.8461, 27.3907, 27.0053 | 27.3907 |
| 100000 | 250000 | 20361025 | 386.3644, 414.8649, 412.2518, 527.6602, 684.7499 | 414.8649 | 624.9279, 609.4027, 715.0445, 898.3690, 923.7956 | 715.0445 |

For these inputs and this interpreter, Kruskal's median was lower at every size.
The largest size shows substantial timing variability; medians reduce but do not
remove environmental noise. Prim additionally builds undirected adjacency and
performs many Python heap operations; Kruskal uses optimized built-in sorting
plus DSU. This explains a plausible practical difference, not a universal
performance guarantee. Both implementations have near-linear storage and
sorting/heap-dominated worst-case time for these sparse multigraphs.

## Sources and AI acknowledgment

Requirements: supplied `Assignment_3_EN.pdf`, Assignment 3 Graph Algorithms.
Official template reference: https://github.com/RZhaniya/daa-assignment-3-graphs
(link extracted from the PDF; repository contents unavailable during this work).
The implementations use the standard textbook cut/exchange arguments, Kosaraju
two-pass DFS, three-color DFS and topological relaxation as explained above;
no external graph library or copied graph implementation is used.

AI assisted with code review and debugging. 
It helped identify potential errors and suggested ways to resolve them. 
It also supported checking edge cases and interpreting test results.
