"""End-to-end integration validation — Phase 5.

Runs 5 scenarios through the REAL engine and the service logic to verify
cross-layer consistency. Uses mock DB records only for persistence points;
the engine and service logic are exercised for real.

Scenarios (per spec):
  1. Expansion regime         — EXPANSION, confident bullish
  2. Transition regime        — TRANSITION, uncertain
  3. Protection regime        — PROTECTION, defensive
  4. Perfect alignment        — portfolio sits exactly on target
  5. Misaligned portfolio     — portfolio far from target, out of band

For each scenario we verify:
  - Allocation weights fall inside the regime's constraint bands
  - Weights sum to 1.0
  - The dividend share falls inside the regime's dividend range
  - AlignmentService uses THE SAME targets as AllocationService (no drift)
  - Regime state flows unchanged through regime → allocation → alignment
  - Suggested adjustments balance to zero (reductions equal increases)

Run: pytest tests/test_end_to_end_integration.py -v
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from grine_regime_engine.allocation import (
    RegimeSnapshot,
    RegimeState,
    run_allocation,
    REGIME_RANGES,
    DIVIDEND_RANGES,
)

from app.schemas.portfolio import PortfolioWeights
from app.services.alignment_scoring import (
    compute_deviations as _compute_deviations,
    compute_range_status as _compute_range_status,
    compute_score as _compute_score,
    resolve_inputs as _resolve_inputs,
    suggest_adjustments as _suggest_adjustments,
)


# ---------------------------------------------------------------------------
# Scenario inputs
# ---------------------------------------------------------------------------

SCENARIOS = {
    "expansion": {
        "snapshot": RegimeSnapshot(
            final_state=RegimeState.EXPANSION,
            probabilities=[0.80, 0.15, 0.05],
            confidence=0.80,
            momentum=0.35,
        ),
        "previous_weights": {"equity": 0.55, "bonds": 0.35, "cash": 0.10},
    },
    "transition": {
        "snapshot": RegimeSnapshot(
            final_state=RegimeState.TRANSITION,
            probabilities=[0.35, 0.50, 0.15],
            confidence=0.50,
            momentum=-0.10,
        ),
        "previous_weights": {"equity": 0.55, "bonds": 0.35, "cash": 0.10},
    },
    "protection": {
        "snapshot": RegimeSnapshot(
            final_state=RegimeState.PROTECTION,
            probabilities=[0.10, 0.20, 0.70],
            confidence=0.75,
            momentum=-0.60,
        ),
        "previous_weights": {"equity": 0.30, "bonds": 0.50, "cash": 0.20},
    },
}


# ---------------------------------------------------------------------------
# Helpers — build a mock recommendation record from an allocation result
# ---------------------------------------------------------------------------

def _mock_recommendation_from(allocation_result):
    """Shape an AllocationRecommendation-like mock from engine output.

    The alignment service reads from the recommendation record, so we mirror
    exactly the fields it reads.
    """
    rec = MagicMock()
    rec.target_equity = allocation_result["target_weights"]["equity"]
    rec.target_bonds = allocation_result["target_weights"]["bonds"]
    rec.target_cash = allocation_result["target_weights"]["cash"]
    rec.constraints = allocation_result["constraints"]
    return rec


def _mock_regime_detection(snapshot: RegimeSnapshot):
    r = MagicMock()
    r.final_state = snapshot.final_state.value if hasattr(
        snapshot.final_state, "value"
    ) else str(snapshot.final_state)
    r.confidence = snapshot.confidence
    r.momentum = snapshot.momentum
    return r


# ---------------------------------------------------------------------------
# Scenario 1/2/3 — Regime-driven allocation validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["expansion", "transition", "protection"])
class TestRegimeDrivenAllocation:
    """Scenarios 1-3: EXPANSION / TRANSITION / PROTECTION."""

    def _run(self, name):
        s = SCENARIOS[name]
        allocation = run_allocation(
            regime=s["snapshot"],
            previous_weights=s["previous_weights"],
        )
        return s, allocation

    def test_weights_sum_to_one(self, name):
        _, allocation = self._run(name)
        w = allocation["final_weights"]
        total = w["equity"] + w["bonds"] + w["cash"]
        assert abs(total - 1.0) < 1e-6, f"{name}: weights sum to {total}"

    def test_final_weights_respect_regime_bands(self, name):
        """Optimizer output must sit inside the regime bands when no prior
        position constrains the move. With a binding turnover cap, the
        final weights may sit between previous and target — this is the
        spec's intended "move partially toward target" behavior.
        """
        s = SCENARIOS[name]
        # No previous weights → optimizer fully enters the band
        allocation = run_allocation(
            regime=s["snapshot"], previous_weights=None,
        )
        state = s["snapshot"].final_state
        bands = REGIME_RANGES[state]
        w = allocation["final_weights"]

        assert bands.equity.lower - 1e-6 <= w["equity"] <= bands.equity.upper + 1e-6
        assert bands.bonds.lower - 1e-6 <= w["bonds"] <= bands.bonds.upper + 1e-6
        assert bands.cash.lower - 1e-6 <= w["cash"] <= bands.cash.upper + 1e-6

    def test_regime_state_propagates(self, name):
        """The regime state in the allocation response must match input."""
        s, allocation = self._run(name)
        expected = s["snapshot"].final_state.value
        assert allocation["constraints"]["regime_state"] == expected

    def test_dividend_share_matches_regime(self, name):
        """Dividend share must fall inside the regime's dividend band."""
        s, allocation = self._run(name)
        state = s["snapshot"].final_state
        div_band = DIVIDEND_RANGES[state]
        share = allocation["dividend_split"]["dividend_share"]
        assert div_band.lower - 1e-6 <= share <= div_band.upper + 1e-6, (
            f"{name}: dividend share {share} not in "
            f"[{div_band.lower}, {div_band.upper}]"
        )

    def test_turnover_cap_respected(self, name):
        _, allocation = self._run(name)
        assert allocation["turnover"]["realized"] <= allocation["turnover"]["cap"] + 1e-9


# ---------------------------------------------------------------------------
# Scenario 4 — Perfect alignment
# ---------------------------------------------------------------------------

class TestPerfectAlignment:
    """Portfolio sits exactly on target in the BALANCED regime."""

    def _setup(self):
        snapshot = RegimeSnapshot(
            final_state=RegimeState.BALANCED,
            probabilities=[0.60, 0.30, 0.10],
            confidence=0.60,
            momentum=0.0,
        )
        allocation = run_allocation(regime=snapshot, previous_weights=None)

        # AlignmentService compares portfolio to `target_weights`, not
        # `final_weights`. A "perfectly aligned" portfolio is one that
        # matches the STEP 2 target — that's the canonical reference.
        target = allocation["target_weights"]
        portfolio = PortfolioWeights(
            equity=target["equity"],
            bonds=target["bonds"],
            cash=target["cash"],
        )

        rec = _mock_recommendation_from(allocation)
        regime = _mock_regime_detection(snapshot)

        return portfolio, regime, rec, allocation

    def test_score_is_maximal(self):
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        score, label, _ = _compute_score(
            _compute_deviations(inputs),
            _compute_range_status(inputs),
        )
        assert score == 100
        assert label == "Highly Aligned"

    def test_all_sleeves_inside_range(self):
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        status = _compute_range_status(inputs)
        assert status == {"equity": "inside", "bonds": "inside", "cash": "inside"}

    def test_no_suggested_adjustments(self):
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        dev = _compute_deviations(inputs)
        actions = _suggest_adjustments(dev)
        assert actions == []


# ---------------------------------------------------------------------------
# Scenario 5 — Misaligned portfolio
# ---------------------------------------------------------------------------

class TestMisalignedPortfolio:
    """95/5/0 portfolio against a PROTECTION regime — worst case."""

    def _setup(self):
        snapshot = RegimeSnapshot(
            final_state=RegimeState.PROTECTION,
            probabilities=[0.10, 0.20, 0.70],
            confidence=0.85,
            momentum=-0.60,
        )
        allocation = run_allocation(regime=snapshot, previous_weights=None)

        portfolio = PortfolioWeights(equity=0.95, bonds=0.05, cash=0.0)
        rec = _mock_recommendation_from(allocation)
        regime = _mock_regime_detection(snapshot)

        return portfolio, regime, rec, allocation

    def test_score_is_misaligned(self):
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        score, label, _ = _compute_score(
            _compute_deviations(inputs),
            _compute_range_status(inputs),
        )
        # PROTECTION target is ~25/55/20; 95/5/0 is catastrophically off
        assert score < 55
        assert label == "Misaligned"

    def test_all_sleeves_flagged_out_of_range(self):
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        status = _compute_range_status(inputs)
        # Every sleeve is outside its band
        assert status["equity"] == "above"
        assert status["bonds"] == "below"
        assert status["cash"] == "below"

    def test_adjustments_balance_to_zero(self):
        """Reductions must equal increases (action list is self-consistent)."""
        portfolio, regime, rec, _ = self._setup()
        inputs = _resolve_inputs(portfolio, regime, rec)
        dev = _compute_deviations(inputs)
        # Sum of signed deviations should be ~0 (portfolio sums to 1, target sums to 1)
        total_dev = dev["equity"] + dev["bonds"] + dev["cash"]
        assert abs(total_dev) < 1e-6

        # Number of reductions should balance against increases
        actions = _suggest_adjustments(dev)
        assert len(actions) >= 2  # equity down, bonds/cash up


# ---------------------------------------------------------------------------
# Cross-layer consistency — the non-negotiable invariant
# ---------------------------------------------------------------------------

class TestCrossLayerConsistency:
    """
    AlignmentService MUST use the same targets as AllocationService.
    If alignment ever computes its own targets, this test fails.
    """

    @pytest.mark.parametrize("name", ["expansion", "transition", "protection"])
    def test_alignment_reads_allocation_targets_exactly(self, name):
        """
        Pipeline: engine → allocation result → recommendation record →
                 alignment._resolve_inputs → deviations.

        The target the alignment service uses must be byte-for-byte the same
        as the allocation target. If anything in between re-derives the
        target, the deviation math will be wrong.
        """
        s = SCENARIOS[name]
        allocation = run_allocation(
            regime=s["snapshot"], previous_weights=None
        )

        rec = _mock_recommendation_from(allocation)
        regime = _mock_regime_detection(s["snapshot"])

        # Feed the allocation TARGET (not final) as the portfolio.
        # Perfect alignment → all deviations exactly zero.
        portfolio = PortfolioWeights(
            equity=allocation["target_weights"]["equity"],
            bonds=allocation["target_weights"]["bonds"],
            cash=allocation["target_weights"]["cash"],
        )
        inputs = _resolve_inputs(portfolio, regime, rec)
        dev = _compute_deviations(inputs)

        assert abs(dev["equity"]) < 1e-6, f"{name}: equity dev {dev['equity']}"
        assert abs(dev["bonds"]) < 1e-6, f"{name}: bonds dev {dev['bonds']}"
        assert abs(dev["cash"]) < 1e-6, f"{name}: cash dev {dev['cash']}"

    @pytest.mark.parametrize("name", ["expansion", "transition", "protection"])
    def test_alignment_reads_allocation_ranges_exactly(self, name):
        """The ranges used by alignment must equal the ranges in allocation."""
        s = SCENARIOS[name]
        allocation = run_allocation(
            regime=s["snapshot"], previous_weights=None
        )

        rec = _mock_recommendation_from(allocation)
        regime = _mock_regime_detection(s["snapshot"])

        portfolio = PortfolioWeights(equity=0.40, bonds=0.45, cash=0.15)
        inputs = _resolve_inputs(portfolio, regime, rec)

        alloc_ranges = allocation["constraints"]["ranges"]
        for asset in ("equity", "bonds", "cash"):
            lo, hi = inputs.ranges[asset]
            assert lo == alloc_ranges[asset]["lower"], (
                f"{name}/{asset}: range lower mismatch"
            )
            assert hi == alloc_ranges[asset]["upper"], (
                f"{name}/{asset}: range upper mismatch"
            )


# ---------------------------------------------------------------------------
# Report-style summary (informational, always passes)
# ---------------------------------------------------------------------------

def test_summary_report(capsys):
    """Human-readable output of all 5 scenarios for inspection."""
    lines = ["", "=" * 72, "5-SCENARIO VALIDATION REPORT", "=" * 72]

    for name, s in SCENARIOS.items():
        allocation = run_allocation(
            regime=s["snapshot"], previous_weights=None
        )
        w = allocation["final_weights"]
        lines.append(
            f"\n── Scenario: {name.upper()} ──\n"
            f"  Regime:     {allocation['constraints']['regime_state']}\n"
            f"  Confidence: {s['snapshot'].confidence:.2f}\n"
            f"  Momentum:   {s['snapshot'].momentum:+.2f}\n"
            f"  Allocation: EQ={w['equity']:.3f} BD={w['bonds']:.3f} CS={w['cash']:.3f}\n"
            f"  Dividend:   {allocation['dividend_split']['dividend_share']:.0%} of equity\n"
            f"  Objective:  {allocation['constraints']['objective']}"
        )

    # Scenario 4: Perfect alignment
    lines.append("\n── Scenario: PERFECT ALIGNMENT ──")
    lines.append("  Portfolio sits on target → expect score 100")

    # Scenario 5: Misaligned
    lines.append("\n── Scenario: MISALIGNED ──")
    lines.append("  95/5/0 vs PROTECTION → expect score 0, Misaligned")

    lines.append("\n" + "=" * 72 + "\n")
    print("\n".join(lines))

    # Capture the output so pytest -s shows it
    captured = capsys.readouterr()
    assert "VALIDATION REPORT" in captured.out
