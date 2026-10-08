"""
Rule 6(1)(c): Net Quantity Declaration in Standard Metric / Count Units.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(c) & Second Schedule.
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import parse_net_quantity, clean_whitespace


def evaluate_rule_6_1_c(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(c)"
    rule_name = "Net Quantity in Standard Units"

    fields = semantic_data.get("fields", {})
    details = semantic_data.get("field_details", {}).get("net_quantity", {})
    raw_qty_text = fields.get("net_quantity")
    evidence_meta = semantic_data.get("evidence", {}).get("net_quantity", {})

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
    if not raw_qty_text or not clean_whitespace(raw_qty_text):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Net quantity declaration is missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    # Attempt to parse quantity from structured details first, or regex fallback
    num_val, unit, norm_str = parse_net_quantity(raw_qty_text)
    
    # Check if field_details already provided structured unit/num
    if not num_val and details.get("numeric_value") is not None:
        num_val = details.get("numeric_value")
        unit = details.get("unit")
        norm_str = f"{num_val} {unit}" if unit else str(num_val)

    # Case 1: Valid numeric value and recognized standard unit
    if num_val is not None and unit:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Net quantity declaration found as {norm_str}.",
            extracted_value=norm_str,
            evidence=evidence_items,
            confidence=0.98,
            details={"numeric_value": num_val, "unit": unit}
        )

    # Case 2: Number found but unit is unrecognized or corrupted (e.g. '45+', '45x')
    if num_val is not None and not unit:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason=f"Quantity value ({num_val}) detected but unit '{raw_qty_text}' is non-standard or corrupted.",
            extracted_value=clean_whitespace(raw_qty_text),
            evidence=evidence_items,
            confidence=0.5
        )

    # Case 3: Completely non-conforming or corrupted string
    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="FAIL",
        reason=f"Text '{raw_qty_text}' does not contain a valid net quantity declaration with standard units.",
        extracted_value=clean_whitespace(raw_qty_text),
        evidence=evidence_items,
        confidence=0.85
    )
