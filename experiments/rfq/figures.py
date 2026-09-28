"""Turn the sweep CSVs into the report's figures.

Every figure in the report is produced here from ``data/raw`` and written into
``report/figures``. No figure is edited by hand, so each one is regenerable with
``make figures``.

Usage:  python3 figures.py --data ../../data/raw --out ../../report/figures
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update(
    {
        "figure.figsize": (5.4, 3.5),
        "font.size": 9,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "savefig.bbox": "tight",
        "savefig.dpi": 200,
    }
)

# Distinguishable without colour: every series has its own marker and dash.
STYLE = {
    "S_no_disclosure": {"marker": "o", "ls": "-", "color": "#1b3a6b", "label": "No disclosure"},
    "S_disclosure": {"marker": "s", "ls": "--", "color": "#b3541e", "label": "Disclosure"},
    "transfer_L": {"marker": "D", "ls": "-", "color": "#1b3a6b", "label": r"Transfer $L$"},
    "kl_information": {"marker": "^", "ls": "-.", "color": "#4a7c59", "label": r"Information $I$ (nats)"},
}


def load(path: Path) -> list[dict]:
    def num(v):
        try:
            return float(v)
        except ValueError:
            return v  # blank first-row step columns, and the boolean flag
    with path.open() as fh:
        return [{k: num(v) for k, v in row.items()} for row in csv.DictReader(fh)]


def _surplus_panel(ax, rows, xkey, xlabel, logx=False):
    x = [r[xkey] for r in rows]
    for key in ("S_no_disclosure", "S_disclosure"):
        ax.plot(x, [r[key] for r in rows], **STYLE[key], markersize=4)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Expected forecaster surplus")
    if logx:
        ax.set_xscale("log")
    ax.legend(loc="best")


def _transfer_panel(ax, rows, xkey, xlabel, logx=False):
    x = [r[xkey] for r in rows]
    ax.errorbar(
        x, [r["transfer_L"] for r in rows],
        yerr=[r["transfer_L_ci95"] for r in rows],
        capsize=2, elinewidth=0.8, markersize=4, **STYLE["transfer_L"],
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(r"Transfer $L$")
    ax.set_ylim(0, None)  # anchored at zero, so a small rise looks small
    if logx:
        ax.set_xscale("log")
    ax2 = ax.twinx()
    kl = [r["kl_information"] for r in rows]
    kl_ci = [r.get("kl_ci95", 0.0) for r in rows]
    ax2.errorbar(x, kl, yerr=kl_ci, capsize=2, elinewidth=0.8, markersize=4,
                 **STYLE["kl_information"])
    ax2.set_ylabel(r"Information $I$ (nats)")
    # Anchor at zero. Without this the axis auto-scales to the noise band and a
    # quantity that is constant by construction reads as a violent trend.
    ax2.set_ylim(0, max(0.2, max(kl) * 1.25))
    ax2.grid(False)
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], loc="best")


def two_panel(rows, xkey, xlabel, out: Path, logx=False):
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4))
    _surplus_panel(axes[0], rows, xkey, xlabel, logx)
    _transfer_panel(axes[1], rows, xkey, xlabel, logx)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    print(f"  -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="../../data/raw")
    ap.add_argument("--out", default="../../report/figures")
    args = ap.parse_args()

    data = Path(args.data).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    two_panel(load(data / "sweep_n.csv"), "n", "Number of responders $n$", out / "sweep_n.pdf")
    two_panel(load(data / "sweep_q.csv"), "q", "Responder signal quality $q$", out / "sweep_q.pdf")
    two_panel(load(data / "sweep_rho.csv"), "rho",
              r"Responder signal dependence $\rho$", out / "sweep_rho.pdf")
    two_panel(
        load(data / "sweep_buckets.csv"), "buckets",
        "Disclosure granularity $B$ (bands)", out / "sweep_buckets.pdf", logx=True,
    )
    two_panel(load(data / "sweep_qf.csv"), "q_f",
              "Forecaster directional accuracy $q_F$", out / "sweep_qf.pdf")
    two_panel(load(data / "sweep_pi.csv"), "pi", r"Public prior $\pi$", out / "sweep_pi.pdf")


if __name__ == "__main__":
    main()
