"""
Data Models for Stage 5: Deterministic Legal Rule Validation.
Strict typing for Rule Evaluations and overall ComplianceResult.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

RuleStatus = Literal["PASS", "FAIL", "UNCERTAIN", "NOT_APPLICABLE"]
OverallStatus = Literal["PASS", "FAIL", "UNCERTAIN"]


class EvidenceItem(BaseModel):
    detection_id: Optional[str] = None
    source_text: Optional[str] = None
    source_image_id: Optional[str] = None
    bounding_box: Optional[Dict[str, int]] = None
    confidence: Optional[float] = None


class RuleEvaluation(BaseModel):
    rule_id: str = Field(..., description="Statutory rule identifier, e.g. '6(1)(a)'")
    rule_name: str = Field(..., description="Human-readable rule name")
    status: RuleStatus = Field(..., description="PASS | FAIL | UNCERTAIN | NOT_APPLICABLE")
    reason: str = Field(..., description="Deterministic explanation of why this verdict was reached")
    extracted_value: Optional[str] = Field(None, description="Cleaned or extracted declaration value")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Source OCR detections supporting this verdict")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in the evaluation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Rule-specific structured details")


class ComplianceSummary(BaseModel):
    total_rules: int = 10
    applicable_rules: int = 0
    passed: int = 0
    failed: int = 0
    uncertain: int = 0
    not_applicable: int = 0


class ComplianceResult(BaseModel):
    package_id: str
    overall_status: OverallStatus
    overall_score: float = Field(..., description="Percentage of passed applicable rules (0.0 to 100.0)")
    summary: ComplianceSummary
    rule_evaluations: List[RuleEvaluation]
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Aggregated evidence across all rules")
