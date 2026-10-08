"""
Rule 6(1)(f): Best Before / Expiry Date.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(f).
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import clean_whitespace

NON_PERISHABLE_KEYWORDS = [
    "earphone", "headphone", "cable", "electronic", "charger", "appliance", 
    "battery", "bulb", "hardware", "tool", "stationary", "pen", "notebook"
]


def evaluate_rule_6_1_f(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(f)"
    rule_name = "Best Before / Expiry Date"

    fields = semantic_data.get("fields", {})
    raw_expiry_text = fields.get("best_before_expiry")
    commodity_name = (fields.get("generic_common_name") or "").lower()
    evidence_meta = semantic_data.get("evidence", {}).get("best_before_expiry", {})

    evidence_items = []
    if evidence_meta and evidence_meta.get("raw_source_text"):
        evidence_items.append(EvidenceItem(
            detection_id=evidence_meta.get("detection_id"),
            source_text=evidence_meta.get("raw_source_text"),
            source_image_id=evidence_meta.get("source_image_id"),
            bounding_box=evidence_meta.get("bounding_box"),
            confidence=evidence_meta.get("ocr_confidence")
        ))

    # Case 1: Expiry / Best Before declaration is explicitly found
    if raw_expiry_text and clean_whitespace(raw_expiry_text):
        cleaned = clean_whitespace(raw_expiry_text)
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Best before / expiry declaration declared: '{cleaned}'.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.95
        )

    # Case 2: Field is absent — check category applicability
    is_non_perishable = any(k in commodity_name for k in NON_PERISHABLE_KEYWORDS)
    if is_non_perishable:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="NOT_APPLICABLE",
            reason=f"Non-perishable commodity ('{commodity_name}'); expiry date is not legally mandatory.",
            extracted_value=None,
            evidence=[],
            confidence=0.98
        )

    # If it is a consumable / food / cosmetic or category unspecified, missing expiry is FAIL
    if commodity_name:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Best before or expiry date declaration is missing on consumable commodity.",
            extracted_value=None,
            evidence=[],
            confidence=0.9
        )

    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="UNCERTAIN",
        reason="Expiry date is missing, and product category cannot be determined with certainty.",
        extracted_value=None,
        evidence=[],
        confidence=0.5
    )
