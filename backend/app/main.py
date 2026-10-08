from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import scan, dashboard, auth

app = FastAPI(
    title="MetroScan Compliance API",
    description="Backend API for Automated Legal Metrology Compliance Verification System",
    version="1.0.0",
)

# ── CORS: Allow Flutter Web and Mobile to connect from anywhere ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins during hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register route modules ──
app.include_router(scan.router, prefix="/api/v1/scan", tags=["Scanning"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.add_api_route("/api/v1/ocr/test", scan.test_ocr_endpoint, methods=["POST"], tags=["OCR Test Pipeline"])


@app.on_event("startup")
async def startup_event():
    import threading
    def _warmup():
        try:
            from app.services.core_engine import get_ocr_reader
            import numpy as np
            r = get_ocr_reader()
            if r:
                r.readtext(np.zeros((100, 100), dtype=np.uint8), min_size=10)
                print("[METROSCAN] OCR reader warmed up successfully and ready for instant inference.")
        except Exception as e:
            print(f"[METROSCAN] OCR warm up notice: {e}")
    threading.Thread(target=_warmup, daemon=True).start()



import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ── Mount static files and web interface ──
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def root():
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "system": "MetroScan Compliance Backend",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "scan": "/api/v1/scan/analyze",
            "dashboard_stats": "/api/v1/dashboard/stats",
            "heatmap": "/api/v1/dashboard/heatmap",
            "recent_scans": "/api/v1/dashboard/recent-scans",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["Health"])
def health_check():
    from app.config import settings
    return {
        "status": "online",
        "mock_mode": settings.USE_MOCK,
        "supabase_configured": bool(settings.SUPABASE_URL),
        "cloudinary_configured": bool(settings.CLOUDINARY_CLOUD_NAME),
    }
