"""
Rule 6(1)(d): Month and Year of Manufacture / Packing / Import.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(d).
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import parse_dates, clean_whitespace


def evaluate_rule_6_1_d(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(d)"
    rule_name = "Month and Year of Manufacture / Packing / Import"

    fields = semantic_data.get("fields", {})
    raw_date_text = fields.get("manufacturing_packing_import_date")
    evidence_meta = semantic_data.get("evidence", {}).get("manufacturing_packing_import_date", {})

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
    if not raw_date_text or not clean_whitespace(raw_date_text):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Month and year of manufacture, packing, or import is missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    cleaned = clean_whitespace(raw_date_text)

    # Check for unreadable digits or wildcards (e.g. '??/26')
    if "??" in cleaned or "xx" in cleaned.lower():
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason=f"Date text '{cleaned}' contains unreadable digits (OCR ambiguity). Manual inspection required.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.5
        )

    # Validate against standard date formats
    dates = parse_dates(cleaned)
    if dates:
        norm_date = dates[0]
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Valid manufacturing/packing/import date found: '{norm_date}'.",
            extracted_value=norm_date,
            evidence=evidence_items,
            confidence=0.96,
            details={"parsed_date": norm_date, "raw_text": cleaned}
        )

    # If contextual label exists but format is non-standard
    if any(k in cleaned.lower() for k in ["mfd", "pkd", "pkg", "import", "packed"]):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Date declaration detected in label: '{cleaned}'.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.85
        )

    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="UNCERTAIN",
        reason=f"Text '{cleaned}' is ambiguous as a manufacturing/packing date.",
        extracted_value=cleaned,
        evidence=evidence_items,
        confidence=0.5
    )
