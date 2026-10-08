"""
Rule 6(1)(h): Country of Origin for Imported Goods.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(h).
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import is_imported_product, clean_whitespace


def evaluate_rule_6_1_h(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(h)"
    rule_name = "Country of Origin for Imported Goods"

    fields = semantic_data.get("fields", {})
    origin_val = fields.get("country_of_origin")
    mfd_val = fields.get("manufacturer_packer_importer")
    evidence_meta = semantic_data.get("evidence", {}).get("country_of_origin", {})

    evidence_items = []
    if evidence_meta and evidence_meta.get("raw_source_text"):
        evidence_items.append(EvidenceItem(
            detection_id=evidence_meta.get("detection_id"),
            source_text=evidence_meta.get("raw_source_text"),
            source_image_id=evidence_meta.get("source_image_id"),
            bounding_box=evidence_meta.get("bounding_box"),
            confidence=evidence_meta.get("ocr_confidence")
        ))

    # Determine import status
    is_imported, import_reason = is_imported_product(mfd_val, origin_val)

    # Case 1: Country of origin is explicitly declared
    if origin_val and clean_whitespace(origin_val):
        cleaned_origin = clean_whitespace(origin_val)
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Country of origin declared as '{cleaned_origin}'.",
            extracted_value=cleaned_origin,
            evidence=evidence_items,
            confidence=0.98,
            details={"country_of_origin": cleaned_origin, "is_imported": is_imported}
        )

    # Case 2: Product indicates imported origin, but Country of Origin is missing
    if is_imported:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"Product indicates imported commodity ({import_reason}), but Country of Origin is not declared.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=0.9,
            details={"is_imported": True}
        )

    # Case 3: Clearly domestic Indian product
    if mfd_val and any(k in mfd_val.lower() for k in ["india", "mumbai", "kolkata", "delhi", "pune", "gujarat", "bengaluru"]):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="NOT_APPLICABLE",
            reason="Domestic Indian manufacturer declared; country of origin rule for imported commodities is not applicable.",
            extracted_value=None,
            evidence=[],
            confidence=0.98,
            details={"is_imported": False}
        )

    # Case 4: Cannot determine whether domestic or imported
    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="NOT_APPLICABLE",
        reason="No indication of import; rule treated as not applicable for standard domestic packaging.",
        extracted_value=None,
        evidence=[],
        confidence=0.8
    )
