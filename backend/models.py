from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AnalyzeRequest(BaseModel):
    text: str
    input_type: str = "text"
    simulated_deepfake_score: Optional[float] = None


# ─────────────────────────────────────────────
# Deepfake
# ─────────────────────────────────────────────
class DeepfakeResult(BaseModel):
    method: str
    model_confidence: float
    anomaly_score: float
    final_deepfake_score: float
    signals: List[str]
    label: str


# ─────────────────────────────────────────────
# Emotion
# ─────────────────────────────────────────────
class EmotionResult(BaseModel):
    dominant_emotion: str
    raw_counts: Dict[str, int]
    density_scores: Dict[str, float]
    stacking_bonus_applied: float
    amplification_score: float


# ─────────────────────────────────────────────
# Propaganda
# ─────────────────────────────────────────────
class PropagandaResult(BaseModel):
    manipulation_score: float
    trigger_phrases: List[str]
    pattern_breakdown: Dict[str, int]


# ─────────────────────────────────────────────
# Virality
# ─────────────────────────────────────────────
class ViralityResult(BaseModel):
    virality_score: float
    multiplier_applied: bool
    multiplier_reason: Optional[str]
    spread_probability: str
    component_breakdown: Dict[str, float]


# ─────────────────────────────────────────────
# PPS
# ─────────────────────────────────────────────
class PPSResult(BaseModel):
    score: float
    threat_level: str
    breakdown: Dict[str, float]
    interaction_effects: Dict[str, Any]
    score_rationale: Dict[str, str]


# ─────────────────────────────────────────────
# SDI
# ─────────────────────────────────────────────
class SDIResult(BaseModel):
    sdi_score: float
    disruption_level: str


# ─────────────────────────────────────────────
# Explainability
# ─────────────────────────────────────────────
class CounterfactualAnalysis(BaseModel):
    pps_without_urgency: float
    pps_without_fear: float
    impact_statement: str


class ExplainabilityResult(BaseModel):
    summary: str
    top_signals: List[str]
    counterfactual_analysis: CounterfactualAnalysis


# ─────────────────────────────────────────────
# Full Response
# ─────────────────────────────────────────────
class AnalysisResult(BaseModel):
    input_type: str
    deepfake: DeepfakeResult
    emotion: EmotionResult
    propaganda: PropagandaResult
    virality: ViralityResult
    pps: PPSResult
    sdi: SDIResult
    pdi: Dict[str, float]
    explanation: ExplainabilityResult
    performance: Dict[str, float]