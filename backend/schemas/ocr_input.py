"""
Pydantic Schemas for OCR Input.
Represents the structured JSON received from the teammate's OCR module.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate in pixels")
    y: int = Field(..., description="Top-left Y coordinate in pixels")
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")


class ImageMetadata(BaseModel):
    image_id: str = Field(..., description="Unique ID for the image file")
    label_side: Literal["front", "back", "side", "top", "bottom", "unspecified"] = "unspecified"
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


class OCRDetection(BaseModel):
    detection_id: str = Field(..., description="Unique detection identifier")
    source_image_id: str = Field(..., description="Image where this text was detected")
    text: str = Field(..., description="Extracted raw text string from OCR")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence score")
    bounding_box: BoundingBox = Field(..., description="Bounding box on the source image")


class ReferenceObject(BaseModel):
    type: str = Field(..., description="e.g. ean_13_barcode, upc_barcode")
    source_image_id: str
    bounding_box: BoundingBox


class OCRInputPayload(BaseModel):
    package_id: str = Field(..., description="Unique identifier for the packaging audit")
    images: List[ImageMetadata] = Field(default_factory=list)
    reference_objects: List[ReferenceObject] = Field(default_factory=list)
    detections: List[OCRDetection] = Field(..., description="List of all detected text regions")
