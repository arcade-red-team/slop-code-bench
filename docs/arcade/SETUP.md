# ARCADE × SlopCodeBench — Setup

This fork measures whether a deterministic architecture guardrail
([arcade-agent](https://arcade-agent.dev), exposed over MCP) changes how coding
agents erode code across SlopCodeBench checkpoints. Nothing here is sent upstream.

## Licenses

| Component | License | Source |
|-----------|---------|--------|
| SlopCodeBench harness (this repo) | MIT | `LICENSE`, upstream `SprocketLab/slop-code-bench` @ `31ceea3` |
| Problem set | see `LICENSE` in the release tarball | `gabeorlanski/scb-problems` release `v1.0` (commit `f87a1fd`) |
| arcade-agent | MIT | PyPI `arcade-agent==0.4.2` |
| Paper | arXiv 2603.24755 v2 (Orlanski et al., 2026) | https://arxiv.org/abs/2603.24755 |

Cite the paper (see `CITATION.cff`) when reporting any number produced here.

## Benchmark version

"v2" in the paper = 36 problems / 196 checkpoints, Python track only. Verified
against the `scb-problems` `v1.0` release: 36 directories with `config.yaml`,
196 `checkpoint_*.md` files (`arcade/select_subset.py` asserts the 36).
Pin the catalog with `SCBENCH_PROBLEMS_PATH` or the managed catalog manifest;
the installed `manifest.json` (version + commit) is recorded per run.

## Infrastructure

From the upstream README and paper Appendix C:

- Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Docker daemon running.
- 8 GB+ RAM, 10 GB+ disk (Docker images + workspaces). First run builds the
  agent image for the pinned harness version (5–10 min).
- Each checkpoint runs in a fresh container as a non-root user; only the working
  directory carries over between checkpoints.
- An Anthropic API key in the environment (`ANTHROPIC_API_KEY`).
- Paper budget: 2 h wall clock per run, no turn or cost cap. The shipped
  `configs/agents/claude_code.yaml` sets `step_limit: 100`; we keep the shipped
  value for all configurations and report it as a deviation.

## Pinned run configuration

| Field | Value | Note |
|-------|-------|------|
| Agent harness | Claude Code `2.1.293` | first release with Claude Haiku 5.5 (paper rule: earliest harness that supports the model) |
| Model | `claude-haiku-5-5` (`configs/models/haiku-5.5.yaml`) | not evaluated in the paper; no published baseline to check against |
| Thinking | `high` → `CLAUDE_CODE_EFFORT_LEVEL=high` | adaptive thinking, effort level (model default is `medium`) |
| Pricing | $0.10 / $0.50 per MTok (prompts ≤100K), $0.50 / $2.50 above | billed cost is taken from Claude Code's own report |
| Temperature | harness default — **not controllable** | Claude Code CLI exposes no temperature flag |
| Seed | **not controllable** | "seed" in this study = replicate index 1..3 |
| Environment | `configs/environments/docker-python3.12-uv.yaml` | |
| Pass policy | `any` (default) | every checkpoint runs; no early stop on failure |
| Prompts | (a) `just-solve`, (b) `anti_slop`, (c) `just-solve` + arcade loop | |

The only true random seed is the pilot subset sampler (seed `2603`), see
`arcade/subset_seed2603.txt`.

## Pilot subset (8 problems, 47 checkpoints)

`random.Random(2603).sample(sorted(problems), 8)` over the v1.0 release:

```
code_search 5
dynamic_config_service_api 4
file_query_tool 5
l2m 5
mvvault 6
recli 8
sith 6
test_translator 8
```
