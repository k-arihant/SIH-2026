"""
Rule 6(1)(e): Maximum Retail Price (MRP) with Mandatory Tax Inclusion Declaration.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(e).
"""

import re
from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import parse_mrp, clean_whitespace


def evaluate_rule_6_1_e(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(e)"
    rule_name = "Maximum Retail Price (MRP) Inclusive of All Taxes"

    fields = semantic_data.get("fields", {})
    details = semantic_data.get("field_details", {}).get("mrp", {})
    raw_mrp_text = fields.get("mrp")
    evidence_meta = semantic_data.get("evidence", {}).get("mrp", {})

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
    if not raw_mrp_text or not clean_whitespace(raw_mrp_text):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Maximum Retail Price (MRP) declaration is missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    cleaned = clean_whitespace(raw_mrp_text)

    # Check for OCR character corruption in price (e.g. letter O for digit 0)
    has_corrupted_zero = bool(
        re.search(r'\b[0-9]*[oO][0-9]*\.[0-9oO]+\b', cleaned) or
        re.search(r'(?:rs\.?|₹)\s*[0-9]*[oO][0-9]*\b', cleaned, re.IGNORECASE) or
        "2o.oo" in cleaned.lower() or "rs o" in cleaned.lower()
    )
    if has_corrupted_zero:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason=f"MRP text '{cleaned}' contains corrupted numeral characters (letter 'O' for '0'). Physical verification required.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.5
        )

    # Parse amount and tax inclusion clause
    amount, has_tax_clause, norm_str = parse_mrp(cleaned)
    
    # Also check structured field_details if available
    if details:
        if details.get("numeric_value") is not None and amount is None:
            amount = float(details.get("numeric_value"))
            norm_str = f"₹ {amount:.2f}"
        if details.get("tax_inclusive_mentioned") is not None:
            has_tax_clause = has_tax_clause or bool(details.get("tax_inclusive_mentioned"))

    if amount is None:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"No valid numeric retail price found in text '{cleaned}'.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.9
        )

    # Check mandatory tax inclusion wording
    if not has_tax_clause:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"MRP declared as {norm_str}, but mandatory 'inclusive of all taxes' statement is missing.",
            extracted_value=norm_str,
            evidence=evidence_items,
            confidence=0.98,
            details={"numeric_value": amount, "tax_inclusive_mentioned": False}
        )

    # Full compliance
    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="PASS",
        reason=f"Valid MRP declaration found: {norm_str} (inclusive of all taxes).",
        extracted_value=f"{norm_str} (incl. of all taxes)",
        evidence=evidence_items,
        confidence=0.98,
        details={"numeric_value": amount, "tax_inclusive_mentioned": True}
    )
