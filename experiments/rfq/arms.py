"""The two arms. Identical in every respect except what responders may condition on.

The forecaster buys one side of a binary contract, in a constant size (see
``model.TRADE_SIZE``). Responders quote competitively and the forecaster takes
the best price available. Per unit:

    buying YES at price P:  payoff Y - P
    buying NO  at price P:  payoff (1 - Y) - P, where P is the NO price

Both arms have ``n`` responders, the same event, the same signals, the same
competition and the same size at risk. The only difference is whether the
``ResponderView`` carries the forecaster's action.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from model import (
    BUY_YES,
    ForecasterState,
    Params,
    ResponderView,
    action_likelihoods,
    draw_event,
    draw_forecaster,
    draw_responder_signals,
    posterior_from_binary,
    responder_quotes,
)


@dataclass(frozen=True)
class ArmResult:
    forecaster_surplus: float
    surplus_samples: object  # per-draw surplus, retained for the paired standard error
    kl_samples: object  # per-draw, per-responder KL, for its standard error
    responder_surplus: float
    mean_price_paid: float
    mean_spread: float
    kl_information: float


def _best_price(quotes: np.ndarray, action_dir: np.ndarray) -> np.ndarray:
    """Price paid under best-of-n posterior quoting.

    Buying YES the forecaster wants the lowest YES quote. Buying NO it pays
    ``1 - price_yes``, so it wants the highest YES quote. Taking the best
    available quote is what makes both arms competitive in the same way, and it
    is also the source of the winner's-selection effect described in
    ``model.responder_quotes``: the selected quote is the most favourable of n
    draws, so the winner is systematically the responder whose signal was most
    misleading in the forecaster's favour.
    """
    return np.where(action_dir == BUY_YES, quotes.min(axis=1), 1.0 - quotes.max(axis=1))


def _kl_bernoulli(p1: np.ndarray, p0: np.ndarray) -> np.ndarray:
    """D_KL(Bern(p1) || Bern(p0)) elementwise, in nats."""
    eps = 1e-12
    p1 = np.clip(p1, eps, 1 - eps)
    p0 = np.clip(p0, eps, 1 - eps)
    return p1 * np.log(p1 / p0) + (1 - p1) * np.log((1 - p1) / (1 - p0))


def run_arm(
    p: Params,
    y: np.ndarray,
    fc: ForecasterState,
    s_j: np.ndarray,
    likelihoods: np.ndarray,
    *,
    disclose: bool,
) -> ArmResult:
    """One arm, on pre-drawn state so both arms see identical randomness."""
    view = ResponderView(
        s_j=s_j,
        action_dir=fc.action_dir if disclose else None,
        action_bucket=fc.action_bucket if disclose else None,
    )
    quotes = responder_quotes(view, p, likelihoods)

    price = _best_price(quotes, fc.action_dir)
    payoff = np.where(fc.action_dir == BUY_YES, y, 1 - y)
    per_unit = payoff - price
    surplus = fc.size * per_unit

    spread = quotes.max(axis=1) - quotes.min(axis=1)

    if disclose:
        without = posterior_from_binary(s_j, p.q, p.pi)
        kl_s = _kl_bernoulli(quotes, without)
    else:
        kl_s = np.zeros_like(quotes)
    kl = float(kl_s.mean())

    return ArmResult(
        surplus_samples=surplus,
        kl_samples=kl_s,
        forecaster_surplus=float(surplus.mean()),
        responder_surplus=float(-surplus.mean()),
        mean_price_paid=float(price.mean()),
        mean_spread=float(spread.mean()),
        kl_information=kl,
    )


@dataclass(frozen=True)
class CellResult:
    params: Params
    disclosure: ArmResult
    no_disclosure: ArmResult

    @property
    def kl_stderr(self) -> float:
        """Standard error of I. It is a Monte Carlo mean, not a direct read."""
        k = self.disclosure.kl_samples
        return float(k.std(ddof=1) / np.sqrt(k.size))

    @property
    def transfer_stderr(self) -> float:
        """Standard error of L.

        Both arms are run on identical randomness, so L is a paired difference
        and its standard error is that of the per-draw difference, not the sum
        of the two arms' errors. Reporting it matters: several sweeps have
        plateaux whose steps are smaller than this, and a plateau that is not
        resolvable must not be presented as one that is.

        NOTE: this is the right error for "is L different from zero in this
        cell". It is the WRONG error for "is L at cell A different from L at
        cell B". Because every cell re-seeds from the same seed, cells in a
        sweep share the realised event and forecaster signal, so a between-cell
        difference is itself paired and its error is far smaller. Use
        ``surplus_samples`` and compare cells directly; ``sweep.py`` does this
        and records it as ``step_ci95``.
        """
        d = self.no_disclosure.surplus_samples - self.disclosure.surplus_samples
        return float(d.std(ddof=1) / np.sqrt(d.size))

    @property
    def transfer(self) -> float:
        """L = S_no-disclosure - S_disclosure.

        A measured quantity with a neutral name. Deliberately not named after
        any conclusion about what it represents; Chapter 6 asks how much of it
        meets the report's definition, and that question must not be settled by
        a variable name.
        """
        return self.no_disclosure.forecaster_surplus - self.disclosure.forecaster_surplus

    def as_row(self) -> dict:
        p = self.params
        return {
            "n": p.n,
            "q": p.q,
            "rho": p.rho,
            "q_f": p.q_f,
            "buckets": p.buckets,
            "pi": p.pi,
            "draws": p.draws,
            "seed": p.seed,
            "S_disclosure": self.disclosure.forecaster_surplus,
            "S_no_disclosure": self.no_disclosure.forecaster_surplus,
            "transfer_L": self.transfer,
            "transfer_L_stderr": self.transfer_stderr,
            "transfer_L_ci95": 1.96 * self.transfer_stderr,
            "kl_information": self.disclosure.kl_information,
            "kl_ci95": 1.96 * self.kl_stderr,
            "responder_surplus_disclosure": self.disclosure.responder_surplus,
            "responder_surplus_no_disclosure": self.no_disclosure.responder_surplus,
            "price_disclosure": self.disclosure.mean_price_paid,
            "price_no_disclosure": self.no_disclosure.mean_price_paid,
            "spread_disclosure": self.disclosure.mean_spread,
            "spread_no_disclosure": self.no_disclosure.mean_spread,
        }


def run_cell(p: Params) -> CellResult:
    """Both arms on one parameter cell, sharing the same drawn randomness."""
    rng = np.random.default_rng(p.seed)
    y = draw_event(rng, p)
    fc = draw_forecaster(rng, p, y)
    s_j = draw_responder_signals(rng, p, y)
    likelihoods = action_likelihoods(p)

    return CellResult(
        params=p,
        disclosure=run_arm(p, y, fc, s_j, likelihoods, disclose=True),
        no_disclosure=run_arm(p, y, fc, s_j, likelihoods, disclose=False),
    )
