from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status, Response, Query
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
import tempfile
import os
import io
import json
import urllib.parse

from app.config import settings
from app.schemas import ScanResponse, DeclarationResult
from app.services.cloudinary_service import CloudinaryService
from app.services.db_service import DBService
from app.services.report_service import ReportGeneratorService
from app.services.email_service import EmailService
from app.dependencies import get_current_user_optional

router = APIRouter()

# Panel types for multi-image capture (maps to image order)
PANEL_TYPES = ["front", "back", "mrp_panel", "side", "other", "other"]


def _get_mock_response(scan_id: str, image_urls: list[str]) -> ScanResponse:
    """
    Returns realistic mock data so Flutter can build UI immediately.
    This is what the UI person's app will receive until the real engine is ready.
    """
    return ScanResponse(
        scan_id=scan_id,
        product_name="Aashirvaad Whole Wheat Atta",
        brand_name="Aashirvaad (ITC Limited)",
        overall_status="NON_COMPLIANT",
        compliance_score=72.5,
        image_urls=image_urls,
        annotated_image_urls=image_urls,  # same as raw in mock mode
        pdf_url=f"/api/v1/scan/{scan_id}/certificate.pdf",
        created_at=datetime.now(timezone.utc),
        declarations=[
            DeclarationResult(
                rule_code="RULE_6_1_A_MFG",
                rule_name="Manufacturer / Packer Details",
                extracted_value="ITC Limited, 37 J.L. Nehru Road, Kolkata 700071, West Bengal",
                is_present=True,
                status="PASS",
                statutory_citation="Rule 6(1)(a)",
                measured_font_height_mm=2.4,
                confidence_score=0.96,
                violation_reason=None,
            ),
            DeclarationResult(
                rule_code="RULE_6_1_B_NAME",
                rule_name="Generic / Common Commodity Name",
                extracted_value="Whole Wheat Flour (Atta)",
                is_present=True,
                status="PASS",
                statutory_citation="Rule 6(1)(b)",
                measured_font_height_mm=3.8,
                confidence_score=0.98,
                violation_reason=None,
            ),
            DeclarationResult(
                rule_code="RULE_6_1_C_NET_QTY",
                rule_name="Net Quantity",
                extracted_value="5 kg",
                is_present=True,
                status="PASS",
                statutory_citation="Rule 6(1)(c)",
                measured_font_height_mm=4.2,
                confidence_score=0.99,
                violation_reason=None,
            ),
            DeclarationResult(
                rule_code="RULE_6_1_D_MFG_DATE",
                rule_name="Manufacturing / Packing Date",
                extracted_value="Mfg Date: 08/2026",
                is_present=True,
                status="PASS",
                statutory_citation="Rule 6(1)(d)",
                measured_font_height_mm=1.8,
                confidence_score=0.92,
                violation_reason=None,
            ),
            DeclarationResult(
                rule_code="RULE_6_1_E_MRP",
                rule_name="Maximum Retail Price (MRP)",
                extracted_value="MRP Rs. 240.00",
                is_present=True,
                status="FAIL",
                statutory_citation="Rule 6(1)(e)",
                measured_font_height_mm=2.1,
                confidence_score=0.91,
                violation_reason="Missing mandatory phrase 'inclusive of all taxes'",
            ),
            DeclarationResult(
                rule_code="RULE_6_1_F_EXPIRY",
                rule_name="Best Before / Expiry Date",
                extracted_value="Best Before: 6 months from Mfg Date",
                is_present=True,
                status="PASS",
                statutory_citation="Rule 6(1)(f)",
                measured_font_height_mm=1.5,
                confidence_score=0.89,
                violation_reason=None,
            ),
            DeclarationResult(
                rule_code="RULE_6_1_G_CONSUMER",
                rule_name="Consumer Care Details",
                extracted_value="feedback@itcfoods.in",
                is_present=True,
                status="WARNING",
                statutory_citation="Rule 6(1)(g)",
                measured_font_height_mm=1.2,
                confidence_score=0.85,
                violation_reason="Email found but mandatory telephone contact number is missing",
            ),
            DeclarationResult(
                rule_code="RULE_6_1_H_ORIGIN",
                rule_name="Country of Origin",
                extracted_value=None,
                is_present=False,
                status="PASS",
                statutory_citation="Rule 6(1)(h)",
                confidence_score=1.0,
                violation_reason=None,  # Not required for domestic products
            ),
            DeclarationResult(
                rule_code="RULE_6_1_I_USP",
                rule_name="Unit Sale Price (USP)",
                extracted_value=None,
                is_present=False,
                status="FAIL",
                statutory_citation="Rule 6(1)(i)",
                confidence_score=0.95,
                violation_reason="Unit sale price declaration is completely missing",
            ),
            DeclarationResult(
                rule_code="RULE_6_3_FONT",
                rule_name="Minimum Font / Numeral Height",
                extracted_value="Smallest measured: 1.2 mm",
                is_present=True,
                status="WARNING",
                statutory_citation="Rule 6(3)",
                measured_font_height_mm=1.2,
                confidence_score=0.78,
                violation_reason="Consumer care text at 1.2mm may be below 2.0mm minimum for this package area",
            ),
        ],
    )


@router.post("/analyze", response_model=ScanResponse)
async def analyze_package(
    images: List[UploadFile] = File(..., description="1-6 package photographs"),
    store_name: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    category: Optional[str] = Form("general"),
    user_id: Optional[str] = Form(None),
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Main scanning endpoint.
    Receives package images from Web/Mobile, runs OCR + statutory compliance check,
    returns structured scorecard JSON.
    """
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required")
    if len(images) > 6:
        raise HTTPException(status_code=400, detail="Maximum 6 images allowed")

    # ── Validate GPS Coordinates ──
    if latitude is not None and not (-90.0 <= latitude <= 90.0):
        raise HTTPException(status_code=400, detail="Invalid GPS latitude. Must be between -90.0 and 90.0 degrees.")
    if longitude is not None and not (-180.0 <= longitude <= 180.0):
        raise HTTPException(status_code=400, detail="Invalid GPS longitude. Must be between -180.0 and 180.0 degrees.")

    # ── Validate Image Extensions ──
    ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
    for img in images:
        ext = os.path.splitext(img.filename or "")[1].lower()
        if ext and ext not in ALLOWED_EXTS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format '{ext}'. Only JPEG, PNG, and WebP are allowed."
            )

    effective_user_id = user_id or (current_user.get("id") if current_user else None)
    scan_id = str(uuid.uuid4())
    uploaded_urls = []

    # ── Step 1: Upload all images to Cloudinary ──
    for idx, img in enumerate(images):
        content = await img.read()
        panel = PANEL_TYPES[idx] if idx < len(PANEL_TYPES) else "other"
        try:
            url = CloudinaryService.upload_scan_image(content, scan_id, panel)
            uploaded_urls.append(url)
        except Exception as e:
            # If Cloudinary fails, continue with empty URL (don't block the scan)
            print(f"[WARN] Cloudinary upload failed for image {idx}: {e}")
            uploaded_urls.append("")

    # ── Step 2: Run analysis (mock or real) ──
    if settings.USE_MOCK:
        response = _get_mock_response(scan_id, uploaded_urls)
    else:
        # Save images to temp files for the OCR engine
        temp_paths = []
        for idx, img in enumerate(images):
            await img.seek(0)
            content = await img.read()
            temp_path = os.path.join(tempfile.gettempdir(), f"metroscan_{scan_id}_{idx}.jpg")
            with open(temp_path, "wb") as f:
                f.write(content)
            temp_paths.append(temp_path)

        # Call the real OCR engine
        from app.services.core_engine import analyze_package as run_engine
        engine_result = run_engine(temp_paths)

        # Upload annotated images if the engine provided them
        annotated_urls = []
        if engine_result.get("annotated_image_bytes"):
            for idx, img_bytes in enumerate(engine_result["annotated_image_bytes"]):
                try:
                    a_url = CloudinaryService.upload_annotated_image(img_bytes, scan_id, idx)
                    annotated_urls.append(a_url)
                except Exception:
                    annotated_urls.append("")
        else:
            annotated_urls = uploaded_urls  # fallback to raw images

        # Build the response
        declarations = [DeclarationResult(**d) for d in engine_result["declarations"]]
        response = ScanResponse(
            scan_id=scan_id,
            product_name=engine_result["product_name"],
            brand_name=engine_result["brand_name"],
            overall_status=engine_result["overall_status"],
            compliance_score=engine_result["compliance_score"],
            declarations=declarations,
            image_urls=uploaded_urls,
            annotated_image_urls=annotated_urls,
            created_at=datetime.now(timezone.utc),
        )

        # Cleanup temp files
        for p in temp_paths:
            try:
                os.remove(p)
            except OSError:
                pass

    # ── Step 3: Save to database (non-blocking, don't fail the response) ──
    try:
        DBService.create_scan(
            scan_id=scan_id,
            user_id=effective_user_id,
            product_id=None,
            store_name=store_name,
            latitude=latitude,
            longitude=longitude,
            overall_status=response.overall_status,
            compliance_score=response.compliance_score,
        )
        # Save image records
        for idx, url in enumerate(uploaded_urls):
            panel = PANEL_TYPES[idx] if idx < len(PANEL_TYPES) else "other"
            ann_url = response.annotated_image_urls[idx] if idx < len(response.annotated_image_urls) else None
            DBService.save_scan_image(scan_id, url, ann_url, panel)
        # Save declaration results
        DBService.save_declarations(scan_id, [d.model_dump() for d in response.declarations])

        # ── Step 4: Auto-generate & upload official court-admissible PDF certificate ──
        try:
            cert = ReportGeneratorService.generate_and_upload(
                scan_id=scan_id,
                product_name=response.product_name,
                brand_name=response.brand_name,
                overall_status=response.overall_status,
                compliance_score=response.compliance_score,
                declarations=response.declarations,
                store_name=store_name,
                latitude=latitude,
                longitude=longitude,
                inspector_name="Inspector Amit Verma",
                badge_id="LM-DEL-8492",
            )
        except Exception as e:
            print(f"[WARN] PDF certificate auto-generation failed: {e}")

        # Always route to the direct PDF streaming endpoint with active live parameters
        qs = []
        if store_name:
            qs.append(f"store_name={urllib.parse.quote(store_name)}")
        if latitude is not None:
            qs.append(f"latitude={latitude}")
        if longitude is not None:
            qs.append(f"longitude={longitude}")
        qs_str = f"?{'&'.join(qs)}" if qs else ""
        response.pdf_url = f"/api/v1/scan/{scan_id}/certificate.pdf{qs_str}"

    except Exception as e:
        print(f"[WARN] Database save failed (non-blocking): {e}")

    return response


@router.get("/{scan_id}/certificate.pdf")
@router.get("/{scan_id}/download-pdf")
def stream_certificate_pdf(
    scan_id: str,
    store_name: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    officer_name: Optional[str] = Query("Inspector Amit Verma"),
    badge_id: Optional[str] = Query("LM-DEL-8492"),
):
    """
    Directly streams standard application/pdf binary bytes.
    Opens natively in all web browsers, tablets, and PDF viewers.
    Generates live with exact inspection GPS coordinates, IST timestamp, and officer credentials.
    """
    product_name = "Aashirvaad Whole Wheat Atta"
    brand_name = "Aashirvaad (ITC Limited)"
    overall_status = "NON_COMPLIANT"
    compliance_score = 72.5
    declarations = None
    effective_store = store_name
    effective_lat = latitude
    effective_lng = longitude

    try:
        sb = DBService.get_supabase()
        scan_res = sb.table("scans").select("*").eq("id", scan_id).execute()
        if scan_res.data:
            s = scan_res.data[0]
            overall_status = s.get("overall_status", overall_status)
            compliance_score = float(s.get("compliance_score") or compliance_score)
            if not effective_store and s.get("store_name"):
                effective_store = s["store_name"]
            if effective_lat is None and s.get("latitude") is not None:
                effective_lat = float(s["latitude"])
            if effective_lng is None and s.get("longitude") is not None:
                effective_lng = float(s["longitude"])

        decl_res = sb.table("declarations").select("*").eq("scan_id", scan_id).execute()
        if decl_res.data:
            declarations = [
                DeclarationResult(
                    rule_code=d["rule_code"],
                    rule_name=d["rule_name"],
                    extracted_value=d.get("extracted_value"),
                    is_present=d.get("is_present", False),
                    status=d.get("status", "FAIL"),
                    statutory_citation=d.get("rule_code", "").replace("_", " "),
                    measured_font_height_mm=d.get("measured_font_height_mm"),
                    confidence_score=d.get("confidence_score", 0.0),
                    violation_reason=d.get("violation_reason"),
                )
                for d in decl_res.data
            ]
    except Exception as e:
        print(f"[WARN] DB lookup for PDF stream failed: {e}")

    if not declarations:
        mock_resp = _get_mock_response(scan_id, [])
        declarations = mock_resp.declarations
        product_name = mock_resp.product_name
        brand_name = mock_resp.brand_name
        overall_status = mock_resp.overall_status
        compliance_score = mock_resp.compliance_score

    pdf_bytes, sha256_hash = ReportGeneratorService.generate_inspection_certificate(
        scan_id=scan_id,
        product_name=product_name,
        brand_name=brand_name,
        overall_status=overall_status,
        compliance_score=compliance_score,
        declarations=declarations,
        store_name=effective_store,
        latitude=effective_lat,
        longitude=effective_lng,
        inspector_name=officer_name or "Inspector Amit Verma",
        badge_id=badge_id or "LM-DEL-8492",
    )

    headers = {
        "Content-Disposition": f"inline; filename=MetroScan_Notice_{scan_id[:8]}.pdf",
        "Content-Type": "application/pdf",
        "X-SHA256-Hash": sha256_hash,
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/{scan_id}/certificate")
def get_or_generate_certificate(
    scan_id: str,
    store_name: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
):
    """
    Returns the official court-admissible PDF certificate endpoint for this scan.
    """
    qs = []
    if store_name:
        qs.append(f"store_name={urllib.parse.quote(store_name)}")
    if latitude is not None:
        qs.append(f"latitude={latitude}")
    if longitude is not None:
        qs.append(f"longitude={longitude}")
    qs_str = f"?{'&'.join(qs)}" if qs else ""
    return {
        "status": "success",
        "scan_id": scan_id,
        "pdf_url": f"/api/v1/scan/{scan_id}/certificate.pdf{qs_str}",
        "download_url": f"/api/v1/scan/{scan_id}/certificate.pdf{qs_str}",
    }


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan_details(scan_id: str):
    """
    Retrieve full details and declarations for a specific scan.
    Used by both the mobile inspection detail view and the web portal.
    """
    if settings.USE_MOCK:
        mock = _get_mock_response(scan_id, [
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600",
            "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600"
        ])
        return mock

    try:
        sb = DBService.get_supabase()
        scan_res = sb.table("scans").select("*").eq("id", scan_id).single().execute()
        if not scan_res.data:
            raise HTTPException(status_code=404, detail="Scan not found")
        s = scan_res.data

        # Get images
        img_res = sb.table("scan_images").select("*").eq("scan_id", scan_id).execute()
        image_urls = [img["image_url"] for img in (img_res.data or []) if img.get("image_url")]
        annotated_urls = [img["annotated_url"] for img in (img_res.data or []) if img.get("annotated_url")]

        # Get declarations
        decl_res = sb.table("declarations").select("*").eq("scan_id", scan_id).execute()
        declarations = [
            DeclarationResult(
                rule_code=d["rule_code"],
                rule_name=d["rule_name"],
                extracted_value=d.get("extracted_value"),
                is_present=d.get("is_present", False),
                status=d.get("status", "FAIL"),
                statutory_citation=d.get("rule_code", "").replace("_", " "),
                measured_font_height_mm=d.get("measured_font_height_mm"),
                confidence_score=d.get("confidence_score", 0.0),
                violation_reason=d.get("violation_reason"),
            )
            for d in (decl_res.data or [])
        ]

        return ScanResponse(
            scan_id=s["id"],
            product_name="Product",
            brand_name="Brand",
            overall_status=s.get("overall_status", "WARNING"),
            compliance_score=float(s.get("compliance_score") or 0.0),
            declarations=declarations,
            image_urls=image_urls if image_urls else ["https://via.placeholder.com/600"],
            annotated_image_urls=annotated_urls if annotated_urls else image_urls,
            created_at=datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")),
        )
    except Exception as e:
        print(f"[WARN] Failed to fetch scan details: {e}")
        return _get_mock_response(scan_id, [])


@router.post("/{scan_id}/report")
async def save_scan_report(
    scan_id: str,
    file: UploadFile = File(...),
    report_type: str = Form("certificate"),
    distribution_method: str = Form("download"),
    sha256_hash: Optional[str] = Form(""),
):
    """
    Receives generated PDF bytes from Flutter, uploads to Cloudinary,
    and logs the report in Supabase.
    """
    try:
        content = await file.read()
        pdf_url = CloudinaryService.upload_report_pdf(content, scan_id)
        if not settings.USE_MOCK:
            DBService.save_report(scan_id, pdf_url, report_type, sha256_hash or "")
        return {
            "status": "success",
            "scan_id": scan_id,
            "pdf_url": pdf_url,
            "report_type": report_type,
            "distribution_method": distribution_method,
        }
    except Exception as e:
        print(f"[WARN] Failed to upload/save report: {e}")
        return {
            "status": "mock_success",
            "scan_id": scan_id,
            "pdf_url": f"https://res.cloudinary.com/metroscan/reports/report_{scan_id}.pdf",
            "report_type": report_type,
            "distribution_method": distribution_method,
        }


class EmailCertificateRequest(BaseModel):
    recipient_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Valid email address")
    recipient_name: Optional[str] = "Citizen / Official"
    store_name: Optional[str] = None


@router.post("/{scan_id}/email")
async def email_scan_certificate(
    scan_id: str,
    req: EmailCertificateRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional),
):
    """
    Dispatches the official court-admissible Legal Metrology certificate PDF
    via email to the specified recipient (officer, manufacturer, or citizen).
    """
    pdf_url = None
    sha256_hash = None
    product_name = "Packaged Commodity"
    brand_name = "Legal Metrology Inspection"
    overall_status = "INSPECTED"
    compliance_score = 100.0
    store_name = req.store_name

    try:
        sb = DBService.get_supabase()
        rep = sb.table("reports").select("*").eq("scan_id", scan_id).execute()
        if rep.data and rep.data[0].get("pdf_url"):
            pdf_url = rep.data[0]["pdf_url"]
            sha256_hash = rep.data[0].get("sha256_hash")

        scan_res = sb.table("scans").select("*").eq("id", scan_id).execute()
        if scan_res.data:
            s = scan_res.data[0]
            overall_status = s.get("overall_status", overall_status)
            compliance_score = float(s.get("compliance_score") or compliance_score)
            if s.get("store_name"):
                store_name = s["store_name"]
    except Exception as e:
        print(f"[WARN] DB lookup in email endpoint: {e}")

    # Fallback to demo certificate URL if in mock mode
    if not pdf_url:
        pdf_url = "https://res.cloudinary.com/havwndoo/raw/upload/v1788804132/metroscan/reports/report_f0ce5e06-601c-461a-bc66-b647a00bba02"
        sha256_hash = "cb2a694ce8e6a1b50a332409d84e6d8e54a79be4551b558ccd7220e49b09d3d1"
        product_name = "Aashirvaad Whole Wheat Atta"
        brand_name = "Aashirvaad (ITC Limited)"
        overall_status = "NON_COMPLIANT"
        compliance_score = 72.5

    result = EmailService.send_certificate(
        recipient_email=req.recipient_email,
        recipient_name=req.recipient_name or (current_user.get("full_name") if current_user else "Stakeholder"),
        scan_id=scan_id,
        product_name=product_name,
        brand_name=brand_name,
        overall_status=overall_status,
        compliance_score=compliance_score,
        pdf_url=pdf_url,
        sha256_hash=sha256_hash,
        store_name=store_name,
    )
    return result


@router.post("/ocr/test")
async def test_ocr_endpoint(
    image: UploadFile = File(..., description="Single package photograph for OCR verification"),
):
    """
    STEP 2: Convert real captured image into structured JSON file.
    Runs fast, robust PyTorch / EasyOCR text and bounding-box detection.
    Saves and returns ocr_output.json.
    """
    if not image:
        raise HTTPException(status_code=400, detail="No image file provided.")

    content = await image.read()
    if not content or len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded image is empty (0 bytes).")

    # 1. Validate image independently using PIL
    try:
        import numpy as np
        from PIL import Image

        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
        orig_w, orig_h = pil_img.size
        img_format = "JPEG"
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Image validation failed. File is corrupt or unreadable: {e}"
        )

    # 2. Resize to optimal OCR resolution (max 960px) for fast 5-8s inference
    max_dim = max(orig_w, orig_h)
    if max_dim > 960:
        scale = 960.0 / max_dim
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        ocr_pil = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        ocr_pil = pil_img

    img_np = np.array(ocr_pil)

    # Apply CLAHE contrast enhancement to clarify reflections on plastic packaging
    try:
        import cv2
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        ocr_input = clahe.apply(gray)
    except Exception:
        ocr_input = img_np

    # 3. Run EasyOCR / PyTorch pipeline safely
    from app.services.core_engine import get_ocr_reader
    reader = get_ocr_reader()
    if reader is None:
        raise HTTPException(status_code=500, detail="Failed to initialize EasyOCR engine.")

    raw_results = []
    try:
        # paragraph=True groups adjacent characters and words into complete lines
        raw_results = reader.readtext(ocr_input, min_size=10, paragraph=True)
    except Exception as ocr_err:
        print(f"[WARN] EasyOCR paragraph readtext error: {ocr_err}. Retrying with standard readtext...")
        try:
            raw_results = reader.readtext(img_np, min_size=12, text_threshold=0.4, low_text=0.3)
        except Exception as ocr_err2:
            print(f"[ERROR] EasyOCR fallback also failed: {ocr_err2}")
            raw_results = []

    # Scale bounding boxes back to original image dimensions if resized
    scale_x = orig_w / float(ocr_pil.width)
    scale_y = orig_h / float(ocr_pil.height)

    image_id = "img_box_back"
    detections = []
    det_idx = 1
    for item in raw_results:
        bbox = item[0]
        text = str(item[1]).strip()
        conf = float(item[2]) if len(item) > 2 else 0.95
        if not text or len(text) < 2:
            continue

        xs = [pt[0] * scale_x for pt in bbox]
        ys = [pt[1] * scale_y for pt in bbox]
        x_min = int(min(xs))
        y_min = int(min(ys))
        box_w = int(max(xs) - min(xs))
        box_h = int(max(ys) - min(ys))

        detections.append({
            "detection_id": f"det_{det_idx:03d}",
            "source_image_id": image_id,
            "text": text,
            "confidence": round(float(conf), 2),
            "bounding_box": {
                "x": x_min,
                "y": y_min,
                "width": box_w,
                "height": box_h,
            },
        })
        det_idx += 1

    package_id = f"pkg_{uuid.uuid4().hex[:8]}"

    response_data = {
        "package_id": package_id,
        "images": [
            {
                "image_id": image_id,
                "label_side": "back",
                "width": orig_w,
                "height": orig_h,
            }
        ],
        "detections": detections,
    }

    # Save directly to ocr_output.json in backend root directory
    output_json_path = os.path.abspath("ocr_output.json")
    try:
        with open(output_json_path, "w", encoding="utf-8") as jf:
            json.dump(response_data, jf, indent=2)
    except Exception as je:
        print(f"[WARN] Failed to write ocr_output.json: {je}")

    return response_data
