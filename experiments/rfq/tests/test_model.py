"""Regression tests. The first is the case computed by hand in Chapter 4."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import model  # noqa: E402
from model import Params, ResponderView, posterior_from_binary, responder_quotes  # noqa: E402


def test_posterior_hand_computed():
    """Two responders, q = 0.75, prior 0.5, one signal each.

    By hand: P(Y=1 | s=1) = (0.5)(0.75) / [(0.5)(0.75) + (0.5)(0.25)] = 0.75,
    and symmetrically P(Y=1 | s=0) = 0.25.
    """
    got = posterior_from_binary(np.array([1, 0]), quality=0.75, prior=0.5)
    assert np.allclose(got, [0.75, 0.25])


def test_prior_shifts_posterior_by_hand():
    """q = 0.6, prior 0.3, s = 1: (0.3)(0.6) / [(0.3)(0.6) + (0.7)(0.4)] = 0.18/0.46."""
    got = posterior_from_binary(np.array([1]), quality=0.6, prior=0.3)
    assert np.allclose(got, [0.18 / 0.46])


def test_action_likelihoods_are_a_distribution():
    """For each Y the action cells must sum to one."""
    p = Params(buckets=5)
    like = model.action_likelihoods(p)
    assert np.allclose(like.sum(axis=(1, 2)), 1.0, atol=1e-4)


@pytest.mark.parametrize("buckets", [1, 2, 4, 8, 16])
def test_action_is_a_strict_coarsening_of_the_posterior(buckets):
    """THE INVARIANT.

    The action must carry strictly less than the posterior. A first version of
    this model used a binary signal, which made the action a lossless encoding
    of it; this test exists so that defect cannot return silently.
    """
    p = Params(buckets=buckets, draws=50_000)
    rng = np.random.default_rng(p.seed)
    y = model.draw_event(rng, p)
    fc = model.draw_forecaster(rng, p, y)

    distinct_actions = len({(d, b) for d, b in zip(fc.action_dir.tolist(), fc.action_bucket.tolist())})
    distinct_posteriors = len(np.unique(np.round(fc.p_f, 6)))

    assert distinct_actions <= 2 * buckets
    assert distinct_posteriors > 10 * distinct_actions


def test_responder_view_cannot_carry_forecaster_state():
    """The invariant, structurally: no field exists through which x or p_f could pass."""
    fields = set(ResponderView.__dataclass_fields__)
    assert fields == {"s_j", "action_dir", "action_bucket"}
    assert not (fields & set(model.ForecasterState.__dataclass_fields__) - {"action_dir", "action_bucket"})


def test_no_disclosure_quotes_ignore_the_action():
    """Quotes in the no-disclosure arm must not move when the action changes."""
    p = Params(n=3, draws=1000)
    like = model.action_likelihoods(p)
    s_j = np.ones((1000, 3), dtype=np.int8)
    a = responder_quotes(ResponderView(s_j=s_j, action_dir=None, action_bucket=None), p, like)
    b = responder_quotes(ResponderView(s_j=s_j, action_dir=None, action_bucket=None), p, like)
    assert np.array_equal(a, b)
    assert np.allclose(a, posterior_from_binary(s_j, p.q, p.pi))


def test_binary_signal_configuration_is_degenerate():
    """Reproduces the defect Chapter 4 reports, so the narrative is checkable.

    The first version of this model gave the forecaster a binary signal and a
    deterministic threshold rule. This reconstructs that configuration and
    asserts the property that made it unusable: the action encodes the signal
    without loss, so a responder conditioning on the action has conditioned on
    the signal. No artefact of the original code survives in the repository,
    so this test is the evidence for the claim.
    """
    rng = np.random.default_rng(20260907)
    draws, q_f, prior = 200_000, 0.75, 0.5

    y = (rng.random(draws) < prior).astype(np.int8)
    s_f = np.where(rng.random(draws) < q_f, y, 1 - y).astype(np.int8)
    p_f = posterior_from_binary(s_f, q_f, prior)
    action = (p_f > 0.5).astype(np.int8)

    assert (action == s_f).mean() == 1.0
    assert len(np.unique(np.round(p_f, 9))) == 2
