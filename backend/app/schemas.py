from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ============================================================
# THE CONTRACT — Every teammate codes against these models.
# Flutter reads this JSON. OCR engine returns this structure.
# DO NOT change field names once teammates start using them.
# ============================================================


class DeclarationResult(BaseModel):
    """One statutory rule check result."""
    rule_code: str                          # e.g., "RULE_6_1_E_MRP"
    rule_name: str                          # e.g., "Maximum Retail Price (MRP)"
    extracted_value: Optional[str] = None   # What the OCR read, or None if missing
    is_present: bool = False                # Was any text found for this rule?
    status: str = "FAIL"                    # "PASS" | "FAIL" | "WARNING"
    statutory_citation: str = ""            # e.g., "Rule 6(1)(e)"
    measured_font_height_mm: Optional[float] = None
    confidence_score: float = 0.0           # 0.0 to 1.0
    violation_reason: Optional[str] = None  # Why it failed, human-readable


class ScanRequest(BaseModel):
    """Metadata sent alongside images (optional fields)."""
    store_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = "general"     # "food" | "cosmetic" | "electronic" | "general"
    user_id: Optional[str] = None


class ScanResponse(BaseModel):
    """The complete result returned to Flutter after scanning."""
    scan_id: str
    product_name: str
    brand_name: str
    overall_status: str                     # "COMPLIANT" | "NON_COMPLIANT" | "WARNING"
    compliance_score: float                 # 0.0 to 100.0
    declarations: List[DeclarationResult]
    image_urls: List[str]                   # Cloudinary URLs of raw uploads
    annotated_image_urls: List[str]         # Cloudinary URLs with bounding box overlays
    pdf_url: Optional[str] = None           # Cloudinary URL of generated official legal notice PDF
    created_at: datetime


class DashboardStats(BaseModel):
    """KPI cards on inspector dashboard & web portal."""
    total_scans: int
    today_scans: int
    violations_detected: int
    compliance_rate: float                  # percentage 0-100
    pending_notices: int


class HeatmapPin(BaseModel):
    """One geo-tagged inspection point on the map."""
    scan_id: str
    latitude: float
    longitude: float
    overall_status: str
    store_name: Optional[str] = None
    product_name: Optional[str] = None
    created_at: datetime


class RecentScan(BaseModel):
    """One row in the scan history table."""
    scan_id: str
    product_name: str
    brand_name: str
    overall_status: str
    compliance_score: float
    store_name: Optional[str] = None
    created_at: datetime
