# ARCADE mode — Design (draft, awaiting approval)

Status: design only. No agent run has been executed; every cost figure below is
an estimate derived from the paper, not a measurement.

## 1. Arcade mode (no scaffold edits)

New agent type `claude_code_arcade`, its own module under
`src/slop_code/agent_runner/agents/claude_code_arcade/`, subclassing
`ClaudeCodeAgent` and registered through `registry.register_agent*`. Upstream
files are untouched except the one-line import in `agents/__init__.py`
(registration side effect).

- **MCP**: own `docker_template` installs `arcade-agent[mcp]==0.4.2` from PyPI
  into an isolated tool venv (`/opt/arcade`), never the workspace venv or
  `requirements.txt`. Attached with `--mcp-config` via `extra_args`.
- **Prompt**: `just-solve` + a short arcade addendum (checkpoint 1: write
  `architecture.spec.json`; later checkpoints: consult `propose_placement` /
  `preview_impact`, keep the contract). (c) vs (a) therefore isolates the
  guardrail, not quality prose.
- **Conformance loop** (post-exit check + resume): after `run(task)` returns,
  the host runs `uvx --from arcade-agent==0.4.2 arcade-guard check <workspace>
  --spec <frozen> --json --no-cache`. On FAIL, the violation list is sent back
  via the existing `_build_cli_args(resume=True)` path, at most `N=2` rounds
  (`arcade_max_repairs`). Each round's verdict appends to
  `arcade_conformance.jsonl`. Must verify `usage` accumulates across resumes.
  Alternative considered: Claude Code Stop hook via `settings` — rejected for
  now because the check would run inside the container with an agent-writable
  spec; revisit if resume accounting breaks.
- **Contract freezing**: after checkpoint 1 the spec is copied to the run
  output dir with its sha256 (`arcade_contract.json`). Later checks always use
  the frozen copy; any change to the workspace spec's hash is logged
  (tampering signal), never trusted.
- **Vacuity guard**: log contract coverage = share of parsed entities assigned
  to some component. Flat single-file solutions may make the contract vacuous
  (always PASS); this is reported as a finding, not tuned away.
- **Workspace hygiene**: parse cache disabled / kept outside the workspace.
  `architecture.spec.json` stays in the workspace (it is the agent's artifact);
  confirm `scb-check` ignores `.json` so LOC/verbosity are unaffected.

## 2. Experiment

| Config | Prompt | Loop |
|--------|--------|------|
| (a) baseline | `just-solve` | — |
| (b) quality prompt | `anti_slop` (paper's quality-guidance prompt) | — |
| (c) arcade | `just-solve` + arcade addendum | conformance, N=2 |

Same model / harness / thinking / environment / problem set (see `SETUP.md`);
3 replicates each. Replicates are not seeded (harness has no seed/temperature).

## 3. Metrics (per checkpoint)

| Metric | Source |
|--------|--------|
| checkpoint pass rate, regression pass rate | built-in `checkpoint_results.jsonl` |
| erosion, verbosity | built-in, pinned `scb-check` |
| cyclomatic complexity (`cc_mean`, `cc_max`, `cc_high_count`) | built-in (radon) |
| maintainability index | **post-hoc** `radon mi` on snapshots, identical for all configs |
| dependency cycles | built-in `graph_cyclic_dependency_mass` (all configs) |
| contract violations, coverage, repair rounds | (c) only; N/A for (a)/(b) |
| P(pass k+1 \| pass k), erosion slope vs checkpoint idx | derived |
| tokens, cost, wall time | built-in inference fields (+ repair rounds for c) |

## 4. Statistics

- Unit = problem. Average replicates within a problem, then bootstrap
  (10,000 resamples, fixed RNG seed) over problems for 95% CIs.
- (c) vs (a) and (c) vs (b): paired per problem, exact Wilcoxon signed-rank
  plus paired permutation test. With 8 problems power is low; stated in
  `RESULTS.md`. Negative and null results are reported.
- Every number in `RESULTS.md` is produced by `arcade/analyze.py` from the
  committed JSONL; the script regenerates the tables and the erosion plot.

## 5. Cost estimate (paper-derived, Sonnet 4.6 ≈ $1.96/checkpoint, ≈14 min/checkpoint)

| Scope | Checkpoints/run | Per run | 9 runs (3 cfg × 3 rep) |
|-------|-----------------|---------|------------------------|
| Pilot subset (8 problems) | 47 | ≈ $92 | ≈ $920–1,000* |
| Full v2 (36 problems) | 196 | ≈ $384 | ≈ $3,600–4,000* |

\* (b) ≈ +12% per paper; (c) assumed +20–50% for repair rounds (unknown until
measured). Wall time ≈ 11 h per subset run sequentially; problems run in
parallel within the Docker/RAM limits.

Proposed spend gates: (1) 1-problem smoke for (a) and (c) ≈ $20;
(2) one (a) replicate on the subset ≈ $92 → re-estimate from measured cost;
(3) full grid only after approval.

## 6. Known confounds / limitations (to carry into RESULTS.md)

- (c) gets extra turns (repairs) → cost and effort confound.
- `step_limit: 100` vs paper's no cap / 2 h wall clock.
- No temperature/seed control; replicate variance is harness-level.
- Single model; Python track only; 8-problem pilot is underpowered.
- arcade-agent's contract is author-written by the same agent being measured.
