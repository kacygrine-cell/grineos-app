// Types mirroring the backend Pydantic schemas.

export type RegimeState =
  | 'EXPANSION'
  | 'BALANCED'
  | 'TRANSITION'
  | 'ENDURANCE'
  | 'PROTECTION';

export type RegimeLabel = 'bull' | 'bear' | 'crisis' | 'recovery' | 'chop';

export type ConfidenceLevel = 'high' | 'moderate' | 'low';

export type AssetClass = 'equity' | 'bonds' | 'cash';

export type OptimizerObjective = 'min_variance' | 'max_sharpe' | 'risk_parity';

export type ChangeMagnitude = 'initial' | 'minor' | 'moderate' | 'major';

// --- Regime ----------------------------------------------------------------

export interface RegimeProbabilities {
  bull: number;
  bear: number;
  crisis: number;
}

export interface RegimeMetadata {
  detector_type: string;
  n_regimes: number;
  data_start_date?: string;
  data_end_date?: string;
  data_points?: number;
  processing_time_ms?: number;
  cache_hit: boolean;
}

export interface RegimeResponse {
  final_state: RegimeState;
  raw_regime?: RegimeLabel;
  confidence: number;       // 0-1
  momentum: number;          // -1 to +1
  probabilities?: RegimeProbabilities;
  metadata: RegimeMetadata;
  detection_id: string;
  tenant_id: string;
  created_at: string;
}

// --- Allocation ------------------------------------------------------------

export interface AllocationWeights {
  equity: number;
  bonds: number;
  cash: number;
}

export interface Range {
  lower: number;
  upper: number;
}

export interface AllocationRanges {
  equity: Range;
  bonds: Range;
  cash: Range;
}

export interface AllocationConstraints {
  regime_state: RegimeState;
  ranges: AllocationRanges;
  turnover_cap: number;
  objective: OptimizerObjective;
  optimizer_status: string;
}

export interface TurnoverInfo {
  realized: number;
  proposed: number;
  cap: number;
  capped: boolean;
}

export interface DividendSplit {
  equity_total: number;
  growth: number;
  dividend: number;
  dividend_share: number;
  range_lower: number;
  range_upper: number;
}

export interface AllocationResponse {
  final_weights: AllocationWeights;
  target_weights: AllocationWeights;
  constraints: AllocationConstraints;
  turnover: TurnoverInfo;
  dividend_split: DividendSplit;
  change_reason?: string;
  change_magnitude?: ChangeMagnitude;
  recommendation_id: string;
  regime_detection_id: string;
  tenant_id: string;
  created_at: string;
  processing_time_ms?: number;
}

export interface AllocationHistoryItem {
  recommendation_id: string;
  weights: AllocationWeights;
  regime_state: RegimeState;
  confidence: number;
  momentum: number;
  turnover: number;
  change_magnitude?: ChangeMagnitude;
  created_at: string;
}

export interface AllocationHistoryResponse {
  current: AllocationResponse;
  history: AllocationHistoryItem[];
  total_count: number;
  date_range: { start?: string; end?: string };
  stats: {
    avg_turnover: number;
    regime_distribution: Record<string, number>;
    rebalance_frequency: number;
  };
}

// --- Portfolio Alignment (server-side — matches backend schema) ------------

export type RangeStatus = 'below' | 'inside' | 'above';
export type AlignmentLabel = 'Highly Aligned' | 'Moderately Aligned' | 'Misaligned';
export type ServerConfidence = 'HIGH' | 'MODERATE' | 'LOW';

export interface AlignmentRegimeContext {
  state: RegimeState;
  confidence: ServerConfidence;
  confidence_value: number;
}

export interface RecommendedContext {
  target: AllocationWeights;
  ranges: {
    equity: [number, number];
    bonds: [number, number];
    cash: [number, number];
  };
}

export interface AlignmentDetail {
  score: number;
  label: AlignmentLabel;
  deviations: {
    equity: number;
    bonds: number;
    cash: number;
  };
  range_status: {
    equity: RangeStatus;
    bonds: RangeStatus;
    cash: RangeStatus;
  };
  penalty_breakdown: Record<string, number>;
}

export interface AlignmentResponse {
  regime: AlignmentRegimeContext;
  portfolio: AllocationWeights;
  recommended: RecommendedContext;
  alignment: AlignmentDetail;
  suggested_adjustments: string[];
  tenant_id: string;
  regime_detection_id?: string;
  recommendation_id?: string;
  processing_time_ms?: number;
}

export interface AlignmentRequest {
  equity: number;
  bonds: number;
  cash: number;
  dividend_equity_share?: number;
  portfolio_id?: string;
  objective?: string;
}
