from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text content to analyze (transcript, post, caption)")
    input_type: str = Field(default="text", description="Input type: text | video | audio")
    # Optional simulated deepfake override (0.0–1.0) for demo purposes
    simulated_deepfake_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional override for deepfake model confidence (demo mode)"
    )


class DeepfakeResult(BaseModel):
    method: str                    # "Hybrid Authenticity Risk Estimation"
    model_confidence: float        # 0–100
    anomaly_score: float           # 0–100
    final_deepfake_score: float    # 0–100 (0.6×MC + 0.4×AH)
    signals: List[str]
    label: str                     # e.g. "[HYBRID] Authenticity Risk"


class EmotionResult(BaseModel):
    dominant_emotion: str
    raw_scores: Dict[str, float]         # fear, anger, urgency, shock, etc.
    weighted_contribution: Dict[str, float]
    amplification_score: float           # 0–100


class PropagandaResult(BaseModel):
    manipulation_score: float            # 0–100
    trigger_phrases: List[str]
    triggered_patterns: List[Dict[str, Any]]   # [{pattern, category, weight}]
    pattern_breakdown: Dict[str, int]    # urgency, authority, polarization, absolutist counts


class ViralityResult(BaseModel):
    virality_score: float               # 0–100
    multiplier_applied: bool
    multiplier_reason: Optional[str]
    spread_probability: str             # Low | Medium | High
    component_breakdown: Dict[str, float]


class PPSBreakdown(BaseModel):
    deepfake_contribution: float
    emotion_contribution: float
    manipulation_contribution: float
    virality_contribution: float


class PPSResult(BaseModel):
    score: float                        # 0–100
    threat_level: str                   # Low / Moderate / High / Severe
    breakdown: PPSBreakdown
    score_rationale: Dict[str, str]     # Module → rationale text


class SDIResult(BaseModel):
    sdi_score: float                    # PPS × (VR / 100)
    disruption_level: str               # Low | Moderate | Severe


class CounterfactualAnalysis(BaseModel):
    pps_without_urgency: float
    pps_without_fear: float
    impact_statement: str


class ExplainabilityResult(BaseModel):
    summary: str
    top_signals: List[str]
    counterfactual_analysis: CounterfactualAnalysis


class AnalysisResult(BaseModel):
    input_type: str
    deepfake: DeepfakeResult
    emotion: EmotionResult
    propaganda: PropagandaResult
    virality: ViralityResult
    pps: PPSResult
    sdi: SDIResult
    explanation: ExplainabilityResult
