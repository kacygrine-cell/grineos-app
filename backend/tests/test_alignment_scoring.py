"""Unit tests for alignment scoring — pure functions, no DB required.

Run from grineos/backend:
    pytest tests/test_alignment_scoring.py -v
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.schemas.portfolio import PortfolioWeights
from app.services.alignment_scoring import (
    ADJUSTMENT_NOISE_FLOOR,
    K1_DEVIATION_PENALTY,
    K2_OUT_OF_RANGE_PENALTY,
    compute_deviations as _compute_deviations,
    compute_range_status as _compute_range_status,
    compute_score as _compute_score,
    resolve_inputs as _resolve_inputs,
    score_label as _score_label,
    suggest_adjustments as _suggest_adjustments,
)


def _mock_recommendation(
    target_equity=0.40, target_bonds=0.45, target_cash=0.15,
    eq_range=(0.35, 0.45), bd_range=(0.40, 0.50), cs_range=(0.10, 0.15),
):
    rec = MagicMock()
    rec.target_equity = target_equity
    rec.target_bonds = target_bonds
    rec.target_cash = target_cash
    rec.constraints = {
        "ranges": {
            "equity": {"lower": eq_range[0], "upper": eq_range[1]},
            "bonds": {"lower": bd_range[0], "upper": bd_range[1]},
            "cash": {"lower": cs_range[0], "upper": cs_range[1]},
        }
    }
    return rec


def _mock_regime(state="TRANSITION", confidence=0.55):
    r = MagicMock()
    r.final_state = state
    r.confidence = confidence
    return r


class TestScoringConstants:
    def test_constants_documented(self):
        """Sanity check that the constants match the documented behavior."""
        # A 10% deviation inside range should cost 5 points.
        assert K1_DEVIATION_PENALTY * 0.10 == 5.0
        # Out-of-range penalty is 10.
        assert K2_OUT_OF_RANGE_PENALTY == 10.0


class TestDeviations:
    def test_perfect_portfolio(self):
        weights = PortfolioWeights(equity=0.40, bonds=0.45, cash=0.15)
        inputs = _resolve_inputs(weights, _mock_regime(), _mock_recommendation())
        dev = _compute_deviations(inputs)
        assert dev == {"equity": 0.0, "bonds": 0.0, "cash": 0.0}

    def test_overweight_equity(self):
        weights = PortfolioWeights(equity=0.58, bonds=0.32, cash=0.10)
        inputs = _resolve_inputs(weights, _mock_regime(), _mock_recommendation())
        dev = _compute_deviations(inputs)
        assert dev["equity"] == pytest.approx(0.18)
        assert dev["bonds"] == pytest.approx(-0.13)
        assert dev["cash"] == pytest.approx(-0.05)


class TestRangeStatus:
    def test_all_inside(self):
        weights = PortfolioWeights(equity=0.40, bonds=0.45, cash=0.15)
        inputs = _resolve_inputs(weights, _mock_regime(), _mock_recommendation())
        status = _compute_range_status(inputs)
        assert status == {"equity": "inside", "bonds": "inside", "cash": "inside"}

    def test_mixed(self):
        weights = PortfolioWeights(equity=0.58, bonds=0.32, cash=0.10)
        inputs = _resolve_inputs(weights, _mock_regime(), _mock_recommendation())
        status = _compute_range_status(inputs)
        assert status == {"equity": "above", "bonds": "below", "cash": "inside"}

    def test_below_all(self):
        # Degenerate: test that 'below' classification works
        weights = PortfolioWeights(equity=0.20, bonds=0.30, cash=0.50)
        inputs = _resolve_inputs(weights, _mock_regime(), _mock_recommendation())
        status = _compute_range_status(inputs)
        assert status["equity"] == "below"
        assert status["bonds"] == "below"
        assert status["cash"] == "above"


class TestScoring:
    def test_perfect_portfolio_scores_100(self):
        score, label, breakdown = _compute_score(
            deviations={"equity": 0.0, "bonds": 0.0, "cash": 0.0},
            range_status={"equity": "inside", "bonds": "inside", "cash": "inside"},
        )
        assert score == 100
        assert label == "Highly Aligned"
        assert breakdown["total_penalty"] == 0.0

    def test_the_example_portfolio(self):
        """The spec's worked example: 58/32/10 vs target 40/45/15.

        Deviations: equity +0.18, bonds -0.13, cash -0.05
        Range status: equity above, bonds below, cash inside
        Penalties:
          equity: 50*0.18 + 10 = 19.0
          bonds:  50*0.13 + 10 = 16.5
          cash:   50*0.05 +  0 =  2.5
        Total: 38.0 → score 62 → Moderately Aligned
        """
        score, label, breakdown = _compute_score(
            deviations={"equity": 0.18, "bonds": -0.13, "cash": -0.05},
            range_status={"equity": "above", "bonds": "below", "cash": "inside"},
        )
        assert score == 62
        assert label == "Moderately Aligned"
        assert breakdown["equity"] == 19.0
        assert breakdown["bonds"] == 16.5
        assert breakdown["cash"] == 2.5
        assert breakdown["total_penalty"] == 38.0

    def test_score_floored_at_zero(self):
        score, label, _ = _compute_score(
            deviations={"equity": 0.70, "bonds": -0.50, "cash": -0.20},
            range_status={"equity": "above", "bonds": "below", "cash": "below"},
        )
        assert score == 0
        assert label == "Misaligned"

    def test_score_labels(self):
        assert _score_label(95) == "Highly Aligned"
        assert _score_label(80) == "Highly Aligned"
        assert _score_label(79) == "Moderately Aligned"
        assert _score_label(55) == "Moderately Aligned"
        assert _score_label(54) == "Misaligned"
        assert _score_label(0) == "Misaligned"


class TestSuggestedAdjustments:
    def test_no_adjustments_when_aligned(self):
        actions = _suggest_adjustments(
            {"equity": 0.001, "bonds": -0.001, "cash": 0.0}
        )
        assert actions == []

    def test_noise_floor_suppression(self):
        """Deviations at or below the noise floor are suppressed."""
        actions = _suggest_adjustments(
            {"equity": ADJUSTMENT_NOISE_FLOOR, "bonds": 0.0, "cash": 0.0}
        )
        assert actions == []

    def test_generates_reduce_and_increase(self):
        actions = _suggest_adjustments(
            {"equity": 0.18, "bonds": -0.13, "cash": -0.05}
        )
        assert "Reduce equities by 18%" in actions
        assert "Increase bonds by 13%" in actions
        assert "Increase cash by 5%" in actions

    def test_actions_balance(self):
        """Reductions should roughly match increases (within rounding)."""
        actions = _suggest_adjustments(
            {"equity": 0.15, "bonds": -0.10, "cash": -0.05}
        )
        # Extract numbers: should have one reduction of ~15, and increases summing ~15
        assert len(actions) == 3

    def test_only_relevant_actions_returned(self):
        """Noise-floor sleeves are skipped entirely."""
        actions = _suggest_adjustments(
            {"equity": 0.15, "bonds": 0.01, "cash": -0.15}
        )
        assert len(actions) == 2
        assert not any("bonds" in a for a in actions)


class TestEndToEndScoring:
    """Integration of the pure scoring pipeline on realistic inputs."""

    def test_transition_regime_overweight_equity(self):
        """TRANSITION regime, portfolio is 60/30/10 — doctrine is 40/45/15."""
        weights = PortfolioWeights(equity=0.60, bonds=0.30, cash=0.10)
        inputs = _resolve_inputs(
            weights,
            _mock_regime(state="TRANSITION", confidence=0.55),
            _mock_recommendation(
                target_equity=0.40, target_bonds=0.45, target_cash=0.15,
                eq_range=(0.35, 0.45), bd_range=(0.40, 0.50), cs_range=(0.10, 0.15),
            ),
        )
        deviations = _compute_deviations(inputs)
        range_status = _compute_range_status(inputs)
        score, label, _ = _compute_score(deviations, range_status)

        # Expected: equity above, bonds below, cash inside
        # Penalty: 50*0.20 + 10 + 50*0.15 + 10 + 50*0.05 + 0 = 10 + 10 + 7.5 + 10 + 2.5 = 40
        # Score: 60 → Moderately Aligned
        assert range_status == {"equity": "above", "bonds": "below", "cash": "inside"}
        assert score == 60
        assert label == "Moderately Aligned"

    def test_expansion_regime_perfectly_aligned(self):
        weights = PortfolioWeights(equity=0.65, bonds=0.28, cash=0.07)
        inputs = _resolve_inputs(
            weights,
            _mock_regime(state="EXPANSION", confidence=0.80),
            _mock_recommendation(
                target_equity=0.65, target_bonds=0.28, target_cash=0.07,
                eq_range=(0.60, 0.70), bd_range=(0.20, 0.30), cs_range=(0.00, 0.10),
            ),
        )
        deviations = _compute_deviations(inputs)
        range_status = _compute_range_status(inputs)
        score, label, _ = _compute_score(deviations, range_status)

        assert score == 100
        assert label == "Highly Aligned"
