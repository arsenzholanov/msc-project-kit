"""Seed-robustness check.

Every number in the Results chapter comes from one realisation at one seed. The
paired intervals capture Monte Carlo error within that realisation and say
nothing about variation across seeds. This script re-runs the sweeps at several
seeds and reports, for each qualitative claim the report makes, whether it holds
at every seed and how far the headline statistics move.

It writes ``data/raw/seed_robustness.csv`` and prints a verdict per claim.

Usage:  python3 seeds.py --seeds 20260907 1 2 3 4 --out ../../data/raw
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from pathlib import Path

from arms import run_cell
from model import Params
from sweep import BASELINE, SWEEPS


def sweep_values(param: str, values: list, seed: int) -> list[float]:
    return [run_cell(replace(BASELINE, seed=seed, **{param: v})).transfer for v in values]


def kl_values(param: str, values: list, seed: int) -> list[float]:
    return [
        run_cell(replace(BASELINE, seed=seed, **{param: v})).disclosure.kl_information
        for v in values
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int,
                    default=[20260907, 11, 22, 33, 44])
    ap.add_argument("--out", default="../../data/raw")
    args = ap.parse_args()

    rows = []
    per_seed: dict[int, dict] = {}

    for seed in args.seeds:
        d = {}
        for stem, (param, values) in SWEEPS.items():
            d[stem] = {"values": values, "L": sweep_values(param, values, seed)}
        d["sweep_buckets"]["I"] = kl_values("buckets", SWEEPS["sweep_buckets"][1], seed)
        per_seed[seed] = d

        base = run_cell(replace(BASELINE, seed=seed))
        L_of = {s: dict(zip(d[s]["values"], d[s]["L"])) for s in d}
        rows.append({
            "seed": seed,
            "baseline_L": base.transfer,
            "baseline_L_ci95": 1.96 * base.transfer_stderr,
            "baseline_share": base.transfer / base.no_disclosure.forecaster_surplus,
            "direction_share": L_of["sweep_buckets"][1] / L_of["sweep_buckets"][64],
            "q_peak": max(L_of["sweep_q"], key=lambda k: L_of["sweep_q"][k]),
            "pi_peak": max(L_of["sweep_pi"], key=lambda k: L_of["sweep_pi"][k]),
            "qf_share_low": None,
            "qf_share_high": None,
            "n_monotone": all(
                b >= a - 1e-9 for a, b in zip(d["sweep_n"]["L"], d["sweep_n"]["L"][1:])
            ),
            "rho_monotone_down": all(
                b <= a + 1e-9 for a, b in zip(d["sweep_rho"]["L"], d["sweep_rho"]["L"][1:])
            ),
            "qf_monotone_up": all(
                b >= a - 1e-9 for a, b in zip(d["sweep_qf"]["L"], d["sweep_qf"]["L"][1:])
            ),
        })

        for qf in (0.55, 0.95):
            c = run_cell(replace(BASELINE, seed=seed, q_f=qf))
            key = "qf_share_low" if qf == 0.55 else "qf_share_high"
            rows[-1][key] = c.transfer / c.no_disclosure.forecaster_surplus
        print(f"  seed {seed} done")

    out = Path(args.out).resolve() / "seed_robustness.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def span(key):
        vals = [r[key] for r in rows]
        return min(vals), max(vals)

    print(f"\nSeeds: {args.seeds}\n")
    print("CLAIM                                            HOLDS AT EVERY SEED   RANGE")
    checks = [
        ("L > 0 at baseline", all(r["baseline_L"] > 0 for r in rows), span("baseline_L")),
        ("L monotone increasing in n", all(r["n_monotone"] for r in rows), None),
        ("L monotone decreasing in rho", all(r["rho_monotone_down"] for r in rows), None),
        ("L monotone increasing in q_f", all(r["qf_monotone_up"] for r in rows), None),
        ("q sweep peaks at q = 0.65", all(r["q_peak"] == 0.65 for r in rows), span("q_peak")),
        ("pi sweep peaks at pi = 0.5", all(r["pi_peak"] == 0.50 for r in rows), span("pi_peak")),
    ]
    for name, ok, rng in checks:
        r = "" if rng is None else f"   {rng[0]:.5g} to {rng[1]:.5g}"
        print(f"  {name:<46} {'yes' if ok else 'NO':<21}{r}")

    print("\nHEADLINE STATISTICS")
    for key, label in [
        ("baseline_L", "baseline L"),
        ("baseline_share", "share of benchmark surplus lost at baseline"),
        ("direction_share", "direction's share of the transfer (B=1 / B=64)"),
        ("qf_share_low", "share lost at q_F = 0.55"),
        ("qf_share_high", "share lost at q_F = 0.95"),
    ]:
        lo, hi = span(key)
        print(f"  {label:<46} {lo:.4f} to {hi:.4f}   (spread {hi - lo:.4f})")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
