"""
Rule 6(1)(i): Unit Sale Price (USP).
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(i).
"""

import re
from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import clean_whitespace


def evaluate_rule_6_1_i(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(i)"
    rule_name = "Unit Sale Price"

    fields = semantic_data.get("fields", {})
    raw_usp_text = fields.get("unit_sale_price")
    net_qty_text = (fields.get("net_quantity") or "").lower()
    evidence_meta = semantic_data.get("evidence", {}).get("unit_sale_price", {})

    evidence_items = []
    if evidence_meta and evidence_meta.get("raw_source_text"):
        evidence_items.append(EvidenceItem(
            detection_id=evidence_meta.get("detection_id"),
            source_text=evidence_meta.get("raw_source_text"),
            source_image_id=evidence_meta.get("source_image_id"),
            bounding_box=evidence_meta.get("bounding_box"),
            confidence=evidence_meta.get("ocr_confidence")
        ))

    # Case 1: Unit Sale Price is declared and valid
    if raw_usp_text and clean_whitespace(raw_usp_text):
        cleaned = clean_whitespace(raw_usp_text)
        
        # Verify it contains rate expression (e.g. '/g', '/kg', '/ml', '/l', 'per g', 'per piece')
        has_rate_format = bool(re.search(r"(?:/|per)\s*(?:100\s*)?[a-zA-Z°]+", cleaned, re.IGNORECASE))
        if has_rate_format:
            return RuleEvaluation(
                rule_id=rule_id,
                rule_name=rule_name,
                status="PASS",
                reason=f"Unit sale price declaration found: '{cleaned}'.",
                extracted_value=cleaned,
                evidence=evidence_items,
                confidence=0.95
            )
        else:
            return RuleEvaluation(
                rule_id=rule_id,
                rule_name=rule_name,
                status="UNCERTAIN",
                reason=f"Unit sale price text '{cleaned}' does not clearly specify a rate per standard unit.",
                extracted_value=cleaned,
                evidence=evidence_items,
                confidence=0.5
            )

    # Case 2: Multi-pack / combo pack detection (e.g. '2 x 150 g', 'combo', 'pack of')
    is_multi_pack = bool(re.search(r"\b(?:\d+\s*x\s*\d+|combo|pack of|save pack)\b", net_qty_text, re.IGNORECASE))
    if is_multi_pack:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"Multi-unit/combo package detected ('{net_qty_text}'), but mandatory Unit Sale Price is missing.",
            extracted_value=None,
            evidence=[],
            confidence=0.9
        )

    # Case 3: Standard single packaging where USP is optional or not mandatory
    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="NOT_APPLICABLE",
        reason="Single-item package declaration; separate unit sale price is not strictly applicable or declared.",
        extracted_value=None,
        evidence=[],
        confidence=0.85
    )
