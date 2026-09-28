"""Core model for the RFQ disclosure experiment.

One binary event, one informed forecaster, ``n`` competing responders.

The structural invariant is enforced by the shape of the code rather than by
care: a responder's quoting function receives a ``ResponderView``, which carries
the responder's own signal and, in the disclosure arm, the forecaster's
*action*. There is no field on it through which the forecaster's private signal
or posterior could travel. ``ForecasterState`` holds those and is never passed
to a responder function.

That structural guarantee is necessary and not sufficient. A first version of
this model gave the forecaster a binary signal and a deterministic threshold
rule, which made the action a lossless encoding of the signal: the responder
obeyed the letter of the invariant and learned the signal exactly. The model
below fixes that at the level of information rather than of interfaces. The
forecaster observes a continuous signal, so the posterior is continuous, and the
action is a genuine coarsening of it: a direction together with a disclosed
confidence band.

The number of bands ``B`` is the disclosure dial and is a first-class swept
parameter. ``B = 1`` discloses direction alone. Large ``B`` approaches full
revelation of the posterior. In a venue that broadcasts the position an informed
forecaster chose, size plays the role of the band, because a forecaster stakes
more when more confident; a venue broadcasting an exact size therefore sits at
the fully-revealing end of this range.

Notation follows Chapter 4 of the report:

    Y       binary event outcome
    pi      public prior, P(Y = 1)
    x       forecaster's continuous private signal
    q_f     forecaster's signal quality; equals the directional accuracy of the
            action only when pi = 0.5, since the prior moves the decision
            threshold away from x = 0
    p_F     forecaster's posterior, P(Y = 1 | x)
    R       forecaster's action: (direction, disclosed confidence band)
    B       number of bands: the disclosure dial
    s_j     responder j's binary private signal
    q       responder signal quality
    rho     correlation among responder signals
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

BUY_YES = 1
BUY_NO = 0

# Traded size is held constant across all cells. An earlier version scaled size
# with the disclosed bucket, which confounded the disclosure dial: raising B both
# revealed more and changed how much the forecaster staked, so the surplus moved
# for two reasons at once. Holding size fixed makes B a pure disclosure dial.
# The cost is that the forecaster's sizing decision is abstracted away; Chapter 4
# states this and Chapter 6 lists it as a limitation.
TRADE_SIZE = 1.0


@dataclass(frozen=True)
class Params:
    """One cell of the sweep."""

    n: int = 5  # responders
    q: float = 0.65  # responder signal quality, in (0.5, 1]
    rho: float = 0.0  # correlation among responder signals, in [0, 1]
    q_f: float = 0.75  # forecaster signal quality, in (0.5, 1]; see module docstring
    buckets: int = 8  # B, the disclosure dial
    pi: float = 0.5  # public prior
    draws: int = 200_000
    seed: int = 20260907

    @property
    def signal_strength(self) -> float:
        """m, such that P(sign of x is correct) == q_f under x | Y ~ N(+/-m, 1).

        The forecaster acts on p_F > 0.5, which is the sign of x only when
        pi = 0.5. At other priors the threshold shifts and q_f no longer equals
        the action's directional accuracy, though m is unchanged. The pi sweep
        therefore varies the prior at fixed signal strength.
        """
        return float(norm.ppf(self.q_f))


@dataclass(frozen=True)
class ForecasterState:
    """The forecaster's private state. Never given to a responder."""

    x: np.ndarray  # continuous private signal
    p_f: np.ndarray  # posterior, P(Y = 1 | x)
    action_dir: np.ndarray  # direction component of R
    action_bucket: np.ndarray  # disclosed confidence band component of R
    size: np.ndarray  # units traded (constant; see TRADE_SIZE)


@dataclass(frozen=True)
class ResponderView:
    """Everything a responder may see.

    In the disclosure arm ``action_dir`` and ``action_bucket`` carry the
    forecaster's request. In the no-disclosure arm both are ``None``. There is
    deliberately no field for ``x`` or ``p_f``.
    """

    s_j: np.ndarray  # shape (draws, n)
    action_dir: np.ndarray | None
    action_bucket: np.ndarray | None


def posterior_from_binary(signal: np.ndarray, quality: float, prior: float) -> np.ndarray:
    """P(Y = 1 | signal) for a binary signal of the given quality."""
    p1 = prior * np.where(signal == 1, quality, 1.0 - quality)
    p0 = (1.0 - prior) * np.where(signal == 1, 1.0 - quality, quality)
    return p1 / (p1 + p0)


def draw_event(rng: np.random.Generator, p: Params) -> np.ndarray:
    return (rng.random(p.draws) < p.pi).astype(np.int8)


def _confidence(p_f: np.ndarray) -> np.ndarray:
    """Distance of the posterior from indifference, mapped to [0, 1)."""
    return np.abs(2.0 * p_f - 1.0)


def _bucket_of(conf: np.ndarray, buckets: int) -> np.ndarray:
    """Coarsen confidence into one of ``buckets`` equal-width bins."""
    idx = np.floor(conf * buckets).astype(np.int64)
    return np.clip(idx, 0, buckets - 1)


def _size_of(bucket: np.ndarray, buckets: int) -> np.ndarray:
    """Traded size. Constant, so that B varies disclosure and nothing else."""
    return np.full(bucket.shape, TRADE_SIZE)


def draw_forecaster(rng: np.random.Generator, p: Params, y: np.ndarray) -> ForecasterState:
    """Continuous signal, continuous posterior, and the coarsened action."""
    m = p.signal_strength
    x = rng.normal(loc=np.where(y == 1, m, -m), scale=1.0)

    # P(Y=1 | x) for x | Y=1 ~ N(m,1), x | Y=0 ~ N(-m,1).
    log_odds = np.log(p.pi / (1.0 - p.pi)) + 2.0 * m * x
    p_f = 1.0 / (1.0 + np.exp(-log_odds))

    action_dir = np.where(p_f > 0.5, BUY_YES, BUY_NO).astype(np.int8)
    bucket = _bucket_of(_confidence(p_f), p.buckets)
    return ForecasterState(
        x=x,
        p_f=p_f,
        action_dir=action_dir,
        action_bucket=bucket,
        size=_size_of(bucket, p.buckets),
    )


def draw_responder_signals(rng: np.random.Generator, p: Params, y: np.ndarray) -> np.ndarray:
    """Exchangeable binary signals of quality ``q`` with correlation ``rho``.

    Mixture construction: with probability ``rho`` a responder copies a single
    common draw, otherwise it draws independently. Every signal is marginally
    correct with probability ``q`` whatever ``rho`` is, so ``rho`` varies the
    dependence between responders without varying how good any one of them is.
    That separation is what makes the rho sweep interpretable.
    """
    common_correct = rng.random(p.draws) < p.q
    s_common = np.where(common_correct, y, 1 - y)

    own_correct = rng.random((p.draws, p.n)) < p.q
    s_own = np.where(own_correct, y[:, None], 1 - y[:, None])

    use_common = rng.random((p.draws, p.n)) < p.rho
    return np.where(use_common, s_common[:, None], s_own).astype(np.int8)


def action_likelihoods(p: Params, grid: int = 20_001) -> np.ndarray:
    """P(R = (d, b) | Y) for each action cell, by numerical integration.

    Returns an array of shape ``(2, 2, buckets)`` indexed
    ``[y, direction, bucket]``. The responder needs these to update on an
    observed action; they depend only on publicly known model parameters, not on
    any realisation of the forecaster's signal.
    """
    m = p.signal_strength
    lo, hi = -8.0 - abs(m), 8.0 + abs(m)
    x = np.linspace(lo, hi, grid)

    log_odds = np.log(p.pi / (1.0 - p.pi)) + 2.0 * m * x
    p_f = 1.0 / (1.0 + np.exp(-log_odds))
    d = np.where(p_f > 0.5, BUY_YES, BUY_NO)
    b = _bucket_of(_confidence(p_f), p.buckets)

    out = np.zeros((2, 2, p.buckets))
    for y_val in (0, 1):
        dens = norm.pdf(x, loc=(m if y_val == 1 else -m), scale=1.0)
        for d_val in (BUY_NO, BUY_YES):
            for b_val in range(p.buckets):
                mask = (d == d_val) & (b == b_val)
                if mask.any():
                    out[y_val, d_val, b_val] = np.trapezoid(dens * mask, x)

    # Guard against a bucket that the grid never reaches.
    out = np.clip(out, 1e-15, None)
    return out


def responder_quotes(view: ResponderView, p: Params, likelihoods: np.ndarray) -> np.ndarray:
    """The price each responder quotes for the YES contract.

    Each responder quotes its own conditional posterior that Y = 1, truthfully.
    In the disclosure arm that posterior additionally conditions on the observed
    action; in the no-disclosure arm it does not. This is the only place a quote
    is formed and it can see nothing beyond ``view`` and publicly known
    parameters.

    NOTE ON WHAT THIS IS NOT. This is truthful posterior quoting, not a Bertrand
    equilibrium. No responder shades its quote, and none anticipates that being
    selected is itself informative: the forecaster takes the best of n quotes, so
    a responder wins precisely when its signal produced an unusually favourable
    price, and its expected profit conditional on winning is worse than its
    unconditional expected profit. A strategic market maker would price that
    selection effect. This model does not, and Chapter 4 says so.
    """
    base = posterior_from_binary(view.s_j, p.q, p.pi)
    if view.action_dir is None or view.action_bucket is None:
        return base

    # Responder signals are independent of the forecaster's signal given Y, so
    # the action's likelihood multiplies in directly.
    like_y1 = likelihoods[1, view.action_dir, view.action_bucket][:, None]
    like_y0 = likelihoods[0, view.action_dir, view.action_bucket][:, None]
    num = base * like_y1
    den = num + (1.0 - base) * like_y0
    return num / den
