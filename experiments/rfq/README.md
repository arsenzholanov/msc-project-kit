# Experiment 1 — RFQ information disclosure

A simulator, not a product. It measures how much of an informed forecaster's
expected surplus moves to responders when responders may condition their quotes
on the forecaster's observed request, against a matched benchmark in which they
may not.

| Module | Responsibility |
|---|---|
| `model.py` | Event, signals, posteriors, quoting, surplus. The frozen model |
| `arms.py` | The two arms, and the metrics: transfer `L`, information `I`, spread, responder surplus |
| `sweep.py` | Parameter grid to `data/raw/` |
| `figures.py` | `data/raw/` to `report/figures/`. No figure is ever edited by hand |
| `tests/test_model.py` | The tiny case computed by hand, held as a regression test |

The one invariant that must not break: **responders observe the forecaster's
action, never the private signal or the posterior.**
