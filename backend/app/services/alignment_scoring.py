"""Pure alignment scoring functions.

Zero I/O, zero DB, zero engine calls. Import-safe without any infrastructure.
This is where the numerical logic lives; `alignment_service.py` is the
orchestration shell that owns persistence and calls these functions.

Separating this module makes the pure/impure boundary explicit and allows
scoring to be unit-tested without spinning up a database.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from app.schemas.portfolio import (
    AlignmentLabel,
    ConfidenceLabel,
    PortfolioWeights,
    RangeStatus,
)


# ---------------------------------------------------------------------------
# Scoring constants (documented, tunable)
# ---------------------------------------------------------------------------

# Linear penalty per unit of absolute deviation from target.
# A 10% drift (0.10) inside range costs 5 points.
K1_DEVIATION_PENALTY: float = 50.0

# Discrete penalty for each sleeve whose weight is outside the regime band.
# Each out-of-band sleeve subtracts an additional 10 points.
K2_OUT_OF_RANGE_PENALTY: float = 10.0

# Threshold below which suggested adjustments are suppressed as noise.
ADJUSTMENT_NOISE_FLOOR: float = 0.02  # 2%

# Classification thresholds.
SCORE_HIGH: int = 80
SCORE_MODERATE: int = 55

ASSETS: Tuple[str, str, str] = ("equity", "bonds", "cash")


# ---------------------------------------------------------------------------
# Lightweight input shapes (no DB records)
# ---------------------------------------------------------------------------

@dataclass
class RegimeLike:
    """Minimum regime attributes needed for scoring. Any object with
    `final_state`, `confidence`, `momentum` can satisfy this."""
    final_state: str
    confidence: float
    momentum: float


@dataclass
class RecommendationLike:
    """Minimum recommendation attributes needed for scoring."""
    target_equity: float
    target_bonds: float
    target_cash: float
    constraints: dict  # must contain "ranges" key


@dataclass
class AlignmentInputs:
    """Resolved inputs for one alignment calculation."""
    portfolio: PortfolioWeights
    target: Dict[str, float]
    ranges: Dict[str, Tuple[float, float]]
    regime: RegimeLike
    recommendation: RecommendationLike


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------

def resolve_inputs(
    portfolio: PortfolioWeights,
    regime,
    recommendation,
) -> AlignmentInputs:
    """Build an AlignmentInputs from any objects providing the expected fields.

    Accepts ORM records, mocks, or the dataclasses above interchangeably.
    """
    target = {
        "equity": recommendation.target_equity,
        "bonds": recommendation.target_bonds,
        "cash": recommendation.target_cash,
    }

    raw_ranges = (
        recommendation.constraints.get("ranges", {})
        if recommendation.constraints else {}
    )
    ranges: Dict[str, Tuple[float, float]] = {}
    for asset in ASSETS:
        r = raw_ranges.get(asset, {})
        ranges[asset] = (
            float(r.get("lower", 0.0)),
            float(r.get("upper", 1.0)),
        )

    return AlignmentInputs(
        portfolio=portfolio,
        target=target,
        ranges=ranges,
        regime=regime,
        recommendation=recommendation,
    )


def compute_deviations(inputs: AlignmentInputs) -> Dict[str, float]:
    """user - target, per sleeve (signed)."""
    p = inputs.portfolio
    t = inputs.target
    return {
        "equity": round(p.equity - t["equity"], 4),
        "bonds":  round(p.bonds  - t["bonds"],  4),
        "cash":   round(p.cash   - t["cash"],   4),
    }


def compute_range_status(inputs: AlignmentInputs) -> Dict[str, RangeStatus]:
    """Classify each sleeve as below / inside / above its regime band."""
    status: Dict[str, RangeStatus] = {}
    weights = {
        "equity": inputs.portfolio.equity,
        "bonds": inputs.portfolio.bonds,
        "cash": inputs.portfolio.cash,
    }
    for asset, w in weights.items():
        lower, upper = inputs.ranges[asset]
        if w < lower - 1e-9:
            status[asset] = "below"
        elif w > upper + 1e-9:
            status[asset] = "above"
        else:
            status[asset] = "inside"
    return status


def compute_score(
    deviations: Dict[str, float],
    range_status: Dict[str, RangeStatus],
) -> Tuple[int, AlignmentLabel, Dict[str, float]]:
    """Apply the transparent scoring:

        score = 100
              - sum over sleeves of K1 * |deviation|
              - K2 per sleeve that is outside its range
        floor at 0, cap at 100.
    """
    breakdown: Dict[str, float] = {}
    penalty = 0.0

    for asset in ASSETS:
        dev_pen = K1_DEVIATION_PENALTY * abs(deviations[asset])
        range_pen = (
            K2_OUT_OF_RANGE_PENALTY
            if range_status[asset] != "inside"
            else 0.0
        )
        sleeve_total = dev_pen + range_pen
        breakdown[asset] = round(sleeve_total, 2)
        penalty += sleeve_total

    score = max(0, min(100, int(round(100.0 - penalty))))
    label = score_label(score)
    breakdown["total_penalty"] = round(penalty, 2)
    return score, label, breakdown


def score_label(score: int) -> AlignmentLabel:
    if score >= SCORE_HIGH:
        return "Highly Aligned"
    if score >= SCORE_MODERATE:
        return "Moderately Aligned"
    return "Misaligned"


def confidence_label(value: float) -> ConfidenceLabel:
    if value >= 0.7:
        return "HIGH"
    if value >= 0.4:
        return "MODERATE"
    return "LOW"


def suggest_adjustments(deviations: Dict[str, float]) -> List[str]:
    """Turn signed deviations into minimal human-readable actions.

    Rules:
      - deviation > +noise  →  "Reduce <asset> by X%"
      - deviation < -noise  →  "Increase <asset> by X%"
      - |deviation| ≤ noise → suppressed
    Actions cancel out (total increases ≈ total decreases).
    """
    labels = {"equity": "equities", "bonds": "bonds", "cash": "cash"}
    actions: List[str] = []
    for asset in ASSETS:
        dev = deviations[asset]
        if abs(dev) <= ADJUSTMENT_NOISE_FLOOR:
            continue
        pct = round(abs(dev) * 100)
        if pct == 0:
            continue
        verb = "Reduce" if dev > 0 else "Increase"
        actions.append(f"{verb} {labels[asset]} by {pct}%")
    return actions
