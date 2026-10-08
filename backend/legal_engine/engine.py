"""
MetroScan Deterministic Legal Rule Validation Engine (Stage 5).
Evaluates structured semantic extraction output against the 10 target Legal Metrology rules.
Pure deterministic Python logic — Gemini does NOT make legal decisions.
"""

from typing import Dict, Any, List, Optional
from backend.legal_engine.models import (
    ComplianceResult,
    RuleEvaluation,
    ComplianceSummary,
    EvidenceItem,
    OverallStatus
)
from backend.legal_engine.rules import ALL_RULE_EVALUATORS


class MetroScanLegalEngine:
    """
    Deterministic Legal Engine for Indian Legal Metrology (Packaged Commodities) Rules, 2011.
    """

    def __init__(self):
        self.rule_evaluators = ALL_RULE_EVALUATORS

    def evaluate(
        self,
        semantic_data: Dict[str, Any],
        ocr_data: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Executes all 10 statutory rules on the input data and computes the overall ComplianceResult.
        """
        package_id = semantic_data.get("package_id") or (ocr_data and ocr_data.get("package_id")) or "unknown_package"
        evaluations: List[RuleEvaluation] = []
        aggregated_evidence: List[EvidenceItem] = []
        seen_det_ids = set()

        # Run each of the 10 deterministic rule evaluators
        for rule_fn in self.rule_evaluators:
            rule_res: RuleEvaluation = rule_fn(semantic_data, ocr_data)
            evaluations.append(rule_res)

            # Collect evidence traceability
            for ev in rule_res.evidence:
                if ev.detection_id and ev.detection_id not in seen_det_ids:
                    seen_det_ids.add(ev.detection_id)
                    aggregated_evidence.append(ev)

        # Compute summary counts
        passed_count = sum(1 for r in evaluations if r.status == "PASS")
        failed_count = sum(1 for r in evaluations if r.status == "FAIL")
        uncertain_count = sum(1 for r in evaluations if r.status == "UNCERTAIN")
        na_count = sum(1 for r in evaluations if r.status == "NOT_APPLICABLE")
        
        applicable_count = len(evaluations) - na_count

        # Explicit overall status logic:
        # 1. If any applicable rule is FAIL -> overall FAIL
        # 2. Else if any applicable rule is UNCERTAIN -> overall UNCERTAIN
        # 3. Else all applicable rules are PASS -> overall PASS
        if failed_count > 0:
            overall_status: OverallStatus = "FAIL"
        elif uncertain_count > 0:
            overall_status: OverallStatus = "UNCERTAIN"
        else:
            overall_status: OverallStatus = "PASS"

        # Explicit score calculation (NOT_APPLICABLE rules do not reduce score)
        if applicable_count > 0:
            score = round((passed_count / applicable_count) * 100.0, 1)
        else:
            score = 100.0

        summary = ComplianceSummary(
            total_rules=len(evaluations),
            applicable_rules=applicable_count,
            passed=passed_count,
            failed=failed_count,
            uncertain=uncertain_count,
            not_applicable=na_count
        )

        return ComplianceResult(
            package_id=package_id,
            overall_status=overall_status,
            overall_score=score,
            summary=summary,
            rule_evaluations=evaluations,
            evidence=aggregated_evidence
        )
