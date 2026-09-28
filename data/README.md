# Data

Sweep outputs written by `experiments/rfq/sweep.py`. Committed, because they are small
and because every figure in the report must be traceable to the run that produced it.

Baseline for every sweep, with one parameter varied at a time:
`n=5, q=0.65, rho=0.0, q_f=0.75, buckets=8, pi=0.5, draws=200000, seed=20260907`.

| File | Varies | Values | Figure |
|---|---|---|---|
| `sweep_n.csv` | `n`, responder count | 1–30 | `report/figures/sweep_n.pdf` |
| `sweep_q.csv` | `q`, responder signal quality | 0.51–0.95 | `report/figures/sweep_q.pdf` |
| `sweep_rho.csv` | `rho`, correlation among responder signals | 0.0–1.0 | `report/figures/sweep_rho.pdf` |
| `sweep_buckets.csv` | `B`, disclosure granularity | 1–64 | `report/figures/sweep_buckets.pdf` |
| `sweep_qf.csv` | `q_f`, forecaster directional accuracy | 0.55–0.95 | `report/figures/sweep_qf.pdf` |
| `sweep_pi.csv` | `pi`, public prior | 0.1–0.9 | `report/figures/sweep_pi.pdf` |
| `seed_robustness.csv` | all six sweeps re-run at five seeds | seeds 20260907, 11, 22, 33, 44 | Table 5.2 |

Every run is seeded and deterministic. Reproduce with `make sweep && make figures`.
Produced 7 September 2026; total runtime about five seconds. Every file records its own
parameters and seed in its columns.

`transfer_L_stderr` and `transfer_L_ci95` are the paired standard error and 95% interval
on `L`. Both arms run on identical randomness, so `L` is a paired difference and its error
is that of the per-draw difference, not the sum of the two arms' errors. Several sweeps
have plateaux whose steps are smaller than this interval.

`step_delta_L`, `step_ci95` and `step_resolved` are the change in `L` from the previous
cell, the paired interval on that change, and whether it resolves. These are the columns to
use when asking whether `L` differs *between* two cells. Cells in a sweep share a seed and
therefore share the realised event and forecaster signal, so a between-cell difference is
itself paired and its interval is roughly an order of magnitude tighter than either cell's
own. Judging a step against a single cell's interval understates the resolving power of the
experiment.

`transfer_L` is the measured quantity `S_no_disclosure - S_disclosure`. The neutral name
is deliberate: how much of it meets the report's definition of AI-MEV is a question for
Chapter 6 and must not be settled by a variable name.
