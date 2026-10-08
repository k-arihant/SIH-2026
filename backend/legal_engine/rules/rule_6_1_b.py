"""
Rule 6(1)(b): Generic or Common Name of Commodity.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(b).
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import clean_whitespace

KNOWN_STANDALONE_BRANDS = {
    "britannia", "nestle", "parle", "amul", "haldiram", "cadbury", "boat", "tata", "colgate", "dettol"
}


def evaluate_rule_6_1_b(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(b)"
    rule_name = "Generic or Common Commodity Name"

    fields = semantic_data.get("fields", {})
    name_val = fields.get("generic_common_name")
    evidence_meta = semantic_data.get("evidence", {}).get("generic_common_name", {})

    evidence_items = []
    if evidence_meta and evidence_meta.get("raw_source_text"):
        evidence_items.append(EvidenceItem(
            detection_id=evidence_meta.get("detection_id"),
            source_text=evidence_meta.get("raw_source_text"),
            source_image_id=evidence_meta.get("source_image_id"),
            bounding_box=evidence_meta.get("bounding_box"),
            confidence=evidence_meta.get("ocr_confidence")
        ))

    # Check for genuine absence
    if not name_val or not clean_whitespace(name_val):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Generic or common commodity name declaration is missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    cleaned = clean_whitespace(name_val)

    # Check if value is merely a brand name alone
    if cleaned.lower() in KNOWN_STANDALONE_BRANDS:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"Brand name '{cleaned}' alone is not sufficient as a generic commodity name.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.9
        )

    # Check for ambiguous text
    if len(cleaned) < 3:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason=f"Commodity name text '{cleaned}' is too brief or ambiguous to verify reliably.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.5
        )

    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="PASS",
        reason=f"Generic commodity name declared: '{cleaned}'.",
        extracted_value=cleaned,
        evidence=evidence_items,
        confidence=0.95
    )
