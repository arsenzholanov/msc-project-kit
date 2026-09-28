"""Run the parameter sweep and write one CSV per swept dimension.

Every run is seeded and deterministic: ``make sweep`` reproduces the files in
``data/raw`` exactly. Each sweep varies one parameter and holds the rest at the
baseline, so a figure reads as one effect rather than several at once.

Usage:  python3 sweep.py --out ../../data/raw
"""

from __future__ import annotations

import argparse
import csv
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from arms import run_cell
from model import Params

BASELINE = Params(n=5, q=0.65, rho=0.0, q_f=0.75, buckets=8, pi=0.5, draws=200_000)

SWEEPS: dict[str, tuple[str, list]] = {
    # file stem            parameter   values
    "sweep_n": ("n", [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]),
    "sweep_q": ("q", [0.51, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
    "sweep_rho": ("rho", [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
    "sweep_buckets": ("buckets", [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]),
    "sweep_qf": ("q_f", [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]),
    "sweep_pi": ("pi", [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]),
}

FIELDS = [
    "n", "q", "rho", "q_f", "buckets", "pi", "draws", "seed",
    "S_disclosure", "S_no_disclosure", "transfer_L", "transfer_L_stderr",
    "transfer_L_ci95", "kl_information", "kl_ci95",
    "responder_surplus_disclosure", "responder_surplus_no_disclosure",
    "price_disclosure", "price_no_disclosure",
    "spread_disclosure", "spread_no_disclosure",
    "step_delta_L", "step_ci95", "step_resolved",
]


def run_sweep(param: str, values: list, out_dir: Path, stem: str) -> None:
    """Run one sweep.

    Alongside each cell's own interval, this records the interval on the STEP
    from the previous cell. Cells in a sweep share a seed and therefore share
    the realised event and forecaster signal, so a between-cell difference is
    itself paired and its error is far tighter than either cell's own. Judging
    "did L change between these two cells" against a single cell's interval
    understates the experiment's resolving power by an order of magnitude.
    """
    rows = []
    prev_cell = None
    for v in values:
        cell = run_cell(replace(BASELINE, **{param: v}))
        row = cell.as_row()

        if prev_cell is None:
            row["step_delta_L"] = ""
            row["step_ci95"] = ""
            row["step_resolved"] = ""
        else:
            a = cell.no_disclosure.surplus_samples - cell.disclosure.surplus_samples
            b = prev_cell.no_disclosure.surplus_samples - prev_cell.disclosure.surplus_samples
            if a.shape == b.shape:
                d = a - b
                ci = 1.96 * float(d.std(ddof=1) / np.sqrt(d.size))
                row["step_delta_L"] = float(d.mean())
                row["step_ci95"] = ci
                row["step_resolved"] = abs(float(d.mean())) > ci
            else:  # shapes differ only if `draws` changed, which no sweep does
                row["step_delta_L"] = ""
                row["step_ci95"] = ""
                row["step_resolved"] = ""

        rows.append(row)
        prev_cell = cell
        r = row
        step = "" if r["step_ci95"] == "" else f"  step={r['step_delta_L']:+.6f}+/-{r['step_ci95']:.6f} {'RES' if r['step_resolved'] else 'unres'}"
        print(
            f"  {param}={v:<6} L={r['transfer_L']:+.5f} +/-{r['transfer_L_ci95']:.5f}  "
            f"KL={r['kl_information']:.5f}{step}"
        )

    path = out_dir / f"{stem}.csv"
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../../data/raw")
    ap.add_argument("--only", default=None, help="run a single sweep by file stem")
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"baseline: {BASELINE}")
    for stem, (param, values) in SWEEPS.items():
        if args.only and stem != args.only:
            continue
        print(f"\n{stem}  (varying {param})")
        t0 = time.time()
        run_sweep(param, values, out_dir, stem)
        print(f"  {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
