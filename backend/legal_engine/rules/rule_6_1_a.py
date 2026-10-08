"""
Rule 6(1)(a): Name and Complete Address of Manufacturer / Packer / Importer.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(a).
"""

from typing import Dict, Any, List
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import clean_whitespace


def evaluate_rule_6_1_a(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(a)"
    rule_name = "Name and Complete Address of Manufacturer / Packer / Importer"

    fields = semantic_data.get("fields", {})
    mfd_val = fields.get("manufacturer_packer_importer")
    evidence_meta = semantic_data.get("evidence", {}).get("manufacturer_packer_importer", {})

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
    if not mfd_val or not clean_whitespace(mfd_val):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Manufacturer, packer, or importer name and address is missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    cleaned = clean_whitespace(mfd_val)

    # Check for heavy truncation or ambiguity
    if "..." in cleaned or len(cleaned) < 10 or (evidence_items and (evidence_items[0].confidence or 1.0) < 0.6):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason="Manufacturer text is truncated, fragmented, or has low OCR confidence. Physical verification required.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.5
        )

    # Valid complete declaration
    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="PASS",
        reason=f"Valid manufacturer/packer/importer declaration found: '{cleaned[:60]}...'",
        extracted_value=cleaned,
        evidence=evidence_items,
        confidence=0.95
    )
