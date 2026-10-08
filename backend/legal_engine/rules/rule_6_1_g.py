"""
Rule 6(1)(g): Consumer Care / Grievance Redressal Details.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(1)(g).
"""

from typing import Dict, Any
from backend.legal_engine.models import RuleEvaluation, EvidenceItem
from backend.legal_engine.normalization import parse_phone_numbers, parse_emails, clean_whitespace


def evaluate_rule_6_1_g(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(1)(g)"
    rule_name = "Consumer Care / Grievance Redressal Details"

    fields = semantic_data.get("fields", {})
    raw_care_text = fields.get("consumer_care")
    evidence_meta = semantic_data.get("evidence", {}).get("consumer_care", {})

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
    if not raw_care_text or not clean_whitespace(raw_care_text):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason="Consumer care / grievance contact details (telephone/toll-free or email) are missing.",
            extracted_value=None,
            evidence=evidence_items,
            confidence=1.0
        )

    cleaned = clean_whitespace(raw_care_text)
    phones = parse_phone_numbers(cleaned)
    emails = parse_emails(cleaned)

    # Valid consumer care if phone, email, or both are found
    if phones or emails:
        contact_parts = []
        if phones:
            contact_parts.append(f"Tel: {', '.join(phones)}")
        if emails:
            contact_parts.append(f"Email: {', '.join(emails)}")
        summary_str = " | ".join(contact_parts)

        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Consumer care details declared ({summary_str}).",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.98,
            details={"phones": phones, "emails": emails}
        )

    # If contextual text mentions care/grievance cell but phone/email extraction was unclear
    if any(k in cleaned.lower() for k in ["consumer care", "customer care", "grievance", "contact:"]):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason=f"Consumer care reference detected ('{cleaned}'), but valid telephone or email could not be parsed.",
            extracted_value=cleaned,
            evidence=evidence_items,
            confidence=0.6
        )

    return RuleEvaluation(
        rule_id=rule_id,
        rule_name=rule_name,
        status="FAIL",
        reason="No valid consumer care phone number or email address found in declaration.",
        extracted_value=cleaned,
        evidence=evidence_items,
        confidence=0.85
    )
