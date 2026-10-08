"""
MetroScan — API Server
"""

import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add paths to sys.path so imports work regardless of working directory
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from backend import config
    from backend.legal_engine import MetroScanLegalEngine
    from backend.extractors.gemini_extractor import GeminiSemanticExtractor
except ImportError:
    import config
    from legal_engine import MetroScanLegalEngine
    from extractors.gemini_extractor import GeminiSemanticExtractor

app = FastAPI(
    title="MetroScan Legal Metrology Compliance API",
    version="1.0.0",
    description="Automated Legal Metrology (Packaged Commodities) Rules 2011 compliance verification engine."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

legal_engine = MetroScanLegalEngine()


@app.on_event("startup")
async def startup():
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    print(f"MetroScan running at http://localhost:{config.PORT}")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "MetroScan Legal Engine",
        "gemini_model": config.GEMINI_MODEL,
        "gemini_configured": bool(config.GEMINI_API_KEY)
    }


@app.post("/api/evaluate")
async def evaluate_compliance(payload: Dict[str, Any] = Body(...)):
    """
    Evaluates packaging declarations against all 10 Legal Metrology statutory rules.
    Takes structured semantic output (and optional raw OCR data) and runs 100% offline.
    """
    try:
        # Check if payload has semantic_data nested or is directly semantic output
        semantic_data = payload.get("semantic_data", payload)
        ocr_data = payload.get("ocr_data", None)

        result = legal_engine.evaluate(semantic_data=semantic_data, ocr_data=ocr_data)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Legal evaluation failed: {str(e)}")


@app.post("/api/analyze")
async def analyze_package(ocr_data: Dict[str, Any] = Body(...)):
    """
    Full pipeline endpoint:
    1. Extracts structured declarations from raw OCR detections via Gemini 3.6 Flash.
    2. Evaluates extracted fields against all 10 Legal Metrology rules deterministically.
    """
    if not config.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured in backend/.env")

    try:
        extractor = GeminiSemanticExtractor(api_key=config.GEMINI_API_KEY)
        semantic_result = extractor.extract(ocr_data)
        compliance_result = legal_engine.evaluate(semantic_data=semantic_result, ocr_data=ocr_data)

        return {
            "package_id": ocr_data.get("package_id", "unknown_package"),
            "semantic_extraction": semantic_result,
            "compliance_evaluation": compliance_result.model_dump()
        }
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            raise HTTPException(status_code=429, detail="Gemini API quota exhausted. Please try again later.")
        elif "503" in err_msg or "UNAVAILABLE" in err_msg:
            raise HTTPException(status_code=503, detail="Gemini model is temporarily experiencing high traffic. Please try again.")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {err_msg}")


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a single product image. Returns saved filename."""
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    saved_name = f"{uuid.uuid4()}{ext}"
    saved_path = os.path.join(config.UPLOAD_DIR, saved_name)

    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    return {
        "filename": saved_name,
        "original_name": file.filename,
        "size_bytes": len(content),
    }


# Serve uploaded images
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
