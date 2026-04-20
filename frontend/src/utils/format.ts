import type { ConfidenceLevel, RegimeState } from '../types';

// --- Number formatting -----------------------------------------------------

export const pct = (v: number, digits = 1) =>
  `${(v * 100).toFixed(digits)}%`;

export const pctNoSign = (v: number, digits = 1) =>
  `${(v * 100).toFixed(digits)}`;

export const signed = (v: number, digits = 1) => {
  const value = (v * 100).toFixed(digits);
  if (v > 0) return `+${value}`;
  return value;
};

// --- Confidence classification --------------------------------------------

export const confidenceLevel = (confidence: number): ConfidenceLevel => {
  if (confidence >= 0.7) return 'high';
  if (confidence >= 0.4) return 'moderate';
  return 'low';
};

export const confidenceLabel = (confidence: number): string => {
  const level = confidenceLevel(confidence);
  return {
    high: 'High Confidence',
    moderate: 'Moderate Confidence',
    low: 'Low Confidence',
  }[level];
};

// --- Momentum interpretation ----------------------------------------------

export const momentumLabel = (momentum: number): string => {
  if (momentum > 0.3) return 'Strong Positive';
  if (momentum > 0.1) return 'Positive';
  if (momentum > -0.1) return 'Neutral';
  if (momentum > -0.3) return 'Negative';
  return 'Strong Negative';
};

export const momentumDirection = (momentum: number): 'up' | 'down' | 'flat' => {
  if (momentum > 0.1) return 'up';
  if (momentum < -0.1) return 'down';
  return 'flat';
};

// --- Regime metadata -------------------------------------------------------

export const regimeNarrative = (state: RegimeState): string => {
  return {
    EXPANSION: 'Growth conditions prevail. Risk assets favored.',
    BALANCED: 'Markets are steady. Balanced positioning warranted.',
    TRANSITION: 'Regime shifting. Reduce risk, build optionality.',
    ENDURANCE: 'Weakness persists. Defensive posture.',
    PROTECTION: 'Stress conditions. Capital preservation priority.',
  }[state];
};

export const regimeColorClass = (state: RegimeState): string => {
  return {
    EXPANSION: 'text-regime-expansion',
    BALANCED: 'text-regime-balanced',
    TRANSITION: 'text-regime-transition',
    ENDURANCE: 'text-regime-endurance',
    PROTECTION: 'text-regime-protection',
  }[state];
};

// --- Time formatting -------------------------------------------------------

export const formatTimestamp = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};
