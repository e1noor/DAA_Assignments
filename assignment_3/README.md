# Assignment 3 — Graph Algorithms

Python 3.12+ implementation using only the standard library. Algorithms:
DSU, Kruskal and Prim minimum spanning forests, Kosaraju SCC, three-state
DFS topological sort, DAG shortest paths and route reconstruction.

## Run and test

From this directory, with a working Python interpreter:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/benchmark.py
python src/main.py < tests/inputs.jsonl
```

No compilation or dependency installation is required. Input/output is UTF-8
JSON Lines, with one result per request and no diagnostic stdout output.
All algorithm state is allocated per call. Deep traversals use explicit stacks.
See `ANALYSIS.md`, `tests/README.md`, and recorded JSON results.

## Required final template integration

The supplied PDF links to https://github.com/RZhaniya/daa-assignment-3-graphs.
That repository could not be retrieved in the preparation environment.
This directory is a standalone implementation of the PDF's contracts, not a
verified copy of the official template. In particular, the ping response
`{"pong": true}` and the minimal manifest `{"language": "Python"}` are local
assumptions until checked against the official adapters and manifest schema.
`tools/run.py` is explicitly a LOCAL runner, not the instructor's checker.
**The 36 official public cases have not been run.**

Before submitting:

1. Create your repository using the official **Use this template** button.
2. Read its complete English/Russian specification and rubric. Transfer these
   algorithm functions into its Python methods, retaining its adapters and ping.
3. Complete the official `submission.json` fields using your real details.
4. Run the OFFICIAL `python tools/run.py --setup` and `--check`; verify its
   **Public checks** Actions workflow passes. Keep this project's custom tests,
   analysis and benchmark results alongside the template tests.
5. Commit the final files and submit the exact GitHub commit URL in Moodle;
   click **Submit assignment**. Grant instructor access if the repository is private.

The source and local checks are prepared for review; the steps above remain
necessary for an assessment-compatible final submission.

## GitHub preparation in the existing assignments repository

The parent repository already has unrelated staged changes. To include only
this assignment, run from the parent directory:

```sh
git add -- assignment_3 .github/workflows/assignment-3.yml
git diff --cached -- assignment_3 .github/workflows/assignment-3.yml
git commit --only -m "Implement assignment 3 graph algorithms" -- assignment_3 .github/workflows/assignment-3.yml
git push origin HEAD
```

This workflow validates the standalone project; it does not substitute for
the instructor's official **Public checks**. This preparation made no commit
and did not push changes. Do the official template integration before Moodle submission.

## Assistance

OpenAI Codex helped review and understand the work and comply with the course AI policy before submission.
