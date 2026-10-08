"""
Rule 6(3): Minimum Height of Numerals and Letters.
Statutory Reference: Legal Metrology (Packaged Commodities) Rules, 2011, Rule 6(3) & Table 1.
"""

from typing import Dict, Any, Optional
from backend.legal_engine.models import RuleEvaluation, EvidenceItem

# Standard EAN-13 Barcode Dimensions under GS1 specifications
STANDARD_EAN13_WIDTH_MM = 37.29
STANDARD_EAN13_HEIGHT_MM = 25.91

# Statutory minimum numeral heights under Rule 6(3) Table 1
def get_statutory_min_height_mm(pdp_area_sq_cm: Optional[float] = None) -> float:
    """
    Legal Metrology (Packaged Commodities) Rules, 2011, Table 1:
      <= 100 cm²        -> >= 1.0 mm
      100 to 500 cm²    -> >= 2.0 mm
      500 to 2500 cm²   -> >= 4.0 mm
      > 2500 cm²        -> >= 6.0 mm
    """
    if pdp_area_sq_cm is None:
        return 2.0  # Default standard retail package
    if pdp_area_sq_cm <= 100:
        return 1.0
    elif pdp_area_sq_cm <= 500:
        return 2.0
    elif pdp_area_sq_cm <= 2500:
        return 4.0
    else:
        return 6.0

DEFAULT_MIN_NUMERAL_HEIGHT_MM = 2.0


def evaluate_rule_6_3(semantic_data: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> RuleEvaluation:
    rule_id = "6(3)"
    rule_name = "Minimum Height of Numerals and Letters"

    ocr_data = ocr_data or {}
    ref_objects = ocr_data.get("reference_objects", [])
    
    # 1. Check if physical measurement already pre-calculated in Stage 3
    stage3_font_info = semantic_data.get("font_measurement") or ocr_data.get("font_measurement")
    if stage3_font_info and stage3_font_info.get("measured_height_mm") is not None:
        measured_mm = float(stage3_font_info["measured_height_mm"])
        min_required = float(stage3_font_info.get("minimum_required_mm", DEFAULT_MIN_NUMERAL_HEIGHT_MM))
        
        if measured_mm >= min_required:
            return RuleEvaluation(
                rule_id=rule_id,
                rule_name=rule_name,
                status="PASS",
                reason=f"Measured numeral height of {measured_mm:.2f} mm meets required minimum threshold ({min_required:.2f} mm).",
                extracted_value=f"{measured_mm:.2f} mm",
                evidence=[],
                confidence=0.9,
                details={"measured_height_mm": measured_mm, "min_required_mm": min_required}
            )
        else:
            return RuleEvaluation(
                rule_id=rule_id,
                rule_name=rule_name,
                status="FAIL",
                reason=f"Measured numeral height of {measured_mm:.2f} mm is below the statutory minimum of {min_required:.2f} mm.",
                extracted_value=f"{measured_mm:.2f} mm",
                evidence=[],
                confidence=0.9,
                details={"measured_height_mm": measured_mm, "min_required_mm": min_required}
            )

    # 2. Check for reference objects (e.g. EAN-13 barcode) in ocr_data
    barcode_ref = None
    for ref in ref_objects:
        if ref.get("type") in ["ean_13_barcode", "barcode", "upc_barcode"]:
            barcode_ref = ref
            break

    if not barcode_ref or not barcode_ref.get("bounding_box"):
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason="No physical reference object (e.g., standard EAN-13 barcode) detected in OCR to establish real-world pixel-to-millimeter scale. Physical inspection required.",
            extracted_value=None,
            evidence=[],
            confidence=0.5
        )

    # 3. Calculate pixels per mm from barcode
    bbox = barcode_ref["bounding_box"]
    barcode_w_px = bbox.get("width", 0)
    if barcode_w_px <= 0:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason="Barcode bounding box has invalid dimensions; cannot calibrate physical scale.",
            extracted_value=None,
            evidence=[],
            confidence=0.5
        )

    pixels_per_mm = barcode_w_px / STANDARD_EAN13_WIDTH_MM

    # Find the primary declaration numeral bounding box (e.g., from Net Qty or MRP evidence)
    evidence_meta = semantic_data.get("evidence", {})
    target_box = None
    target_text = None
    target_det_id = None
    source_img = None

    for field_key in ["net_quantity", "mrp"]:
        ev = evidence_meta.get(field_key)
        if ev and ev.get("bounding_box") and ev["bounding_box"].get("height", 0) > 0:
            target_box = ev["bounding_box"]
            target_text = ev.get("raw_source_text")
            target_det_id = ev.get("detection_id")
            source_img = ev.get("source_image_id")
            break

    if not target_box:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="UNCERTAIN",
            reason="Barcode detected but target numeral bounding box could not be isolated for height measurement.",
            extracted_value=None,
            evidence=[],
            confidence=0.5
        )

    # Calculate measured height in millimetres
    numeral_height_px = target_box.get("height", 0)
    measured_height_mm = numeral_height_px / pixels_per_mm
    pdp_area = semantic_data.get("pdp_area_sq_cm") or ocr_data.get("pdp_area_sq_cm")
    min_required_mm = get_statutory_min_height_mm(pdp_area)

    evidence_items = [
        EvidenceItem(
            detection_id=target_det_id,
            source_text=target_text,
            source_image_id=source_img,
            bounding_box=target_box,
            confidence=0.9
        )
    ]

    if measured_height_mm >= min_required_mm:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="PASS",
            reason=f"Measured declaration numeral height of {measured_height_mm:.2f} mm satisfies minimum threshold ({min_required_mm:.2f} mm) calibrated via barcode.",
            extracted_value=f"{measured_height_mm:.2f} mm",
            evidence=evidence_items,
            confidence=0.92,
            details={
                "measured_height_mm": round(measured_height_mm, 2),
                "minimum_required_mm": min_required_mm,
                "pixels_per_mm": round(pixels_per_mm, 2),
                "calibration_reference": "EAN-13 Barcode (37.29 mm)"
            }
        )
    else:
        return RuleEvaluation(
            rule_id=rule_id,
            rule_name=rule_name,
            status="FAIL",
            reason=f"Measured declaration numeral height of {measured_height_mm:.2f} mm is below the statutory minimum ({min_required_mm:.2f} mm) calibrated via barcode.",
            extracted_value=f"{measured_height_mm:.2f} mm",
            evidence=evidence_items,
            confidence=0.92,
            details={
                "measured_height_mm": round(measured_height_mm, 2),
                "minimum_required_mm": min_required_mm,
                "pixels_per_mm": round(pixels_per_mm, 2),
                "calibration_reference": "EAN-13 Barcode (37.29 mm)"
            }
        )
