"""
Pydantic Schemas for Gemini Structured Product Output.
Strict semantic extraction layer — NO legal PASS/FAIL decisions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.ocr_input import BoundingBox


class EvidenceTrace(BaseModel):
    detection_id: Optional[str] = None
    source_image_id: Optional[str] = None
    raw_source_text: str = Field(..., description="Exact OCR snippet from which this was extracted")
    ocr_confidence: Optional[float] = None
    bounding_box: Optional[BoundingBox] = None


class ExtractedField(BaseModel):
    field_name: str = Field(..., description="Identifier of the field, e.g., 'mrp', 'net_quantity'")
    found: bool = Field(..., description="True if text corresponding to this field exists in OCR")
    normalized_value: Optional[str] = Field(None, description="Cleaned extracted string or structured representation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Fine-grained parsed attributes (e.g. currency, unit)")
    evidence: Optional[EvidenceTrace] = Field(None, description="Back-trace to source OCR bounding box & image")
    gemini_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Extraction confidence")
    uncertain: bool = Field(False, description="True if text is corrupted, ambiguous, or borderline")
    uncertainty_reason: Optional[str] = Field(None, description="Explanation if marked uncertain")


class StructuredProductInformation(BaseModel):
    package_id: str
    
    # 9 Target Legal Declaration Fields
    manufacturer_packer_importer: ExtractedField
    generic_commodity_name: ExtractedField
    net_quantity: ExtractedField
    manufacturing_packing_import_date: ExtractedField
    mrp: ExtractedField
    best_before_expiry: ExtractedField
    consumer_care: ExtractedField
    country_of_origin: ExtractedField
    unit_sale_price: ExtractedField
    
    # Preserved Non-Target / Irrelevant Text
    unclassified_text: List[EvidenceTrace] = Field(
        default_factory=list, 
        description="OCR text blocks that do not map to the 9 mandatory declarations (e.g., ingredients, slogans)"
    )
