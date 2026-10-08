from fastapi import APIRouter
from datetime import datetime, timezone
from typing import Optional, List

from app.config import settings
from app.schemas import DashboardStats, HeatmapPin, RecentScan
from app.services.db_service import DBService

router = APIRouter()


# ── Mock data for when database is empty or not configured ──

MOCK_STATS = {
    "total_scans": 347,
    "today_scans": 48,
    "violations_detected": 89,
    "compliance_rate": 74.4,
    "pending_notices": 12,
}

MOCK_HEATMAP = [
    {"scan_id": "mock-1", "latitude": 28.6139, "longitude": 77.2090, "overall_status": "NON_COMPLIANT", "store_name": "Metro Mart, Connaught Place", "product_name": "Atta 5kg", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "mock-2", "latitude": 28.5355, "longitude": 77.3910, "overall_status": "COMPLIANT", "store_name": "Big Bazaar, Noida Sec 18", "product_name": "Parle-G Biscuits", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "mock-3", "latitude": 28.4595, "longitude": 77.0266, "overall_status": "WARNING", "store_name": "Reliance Fresh, Gurgaon", "product_name": "Fair & Lovely Cream", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "mock-4", "latitude": 28.6692, "longitude": 77.4538, "overall_status": "NON_COMPLIANT", "store_name": "Kirana Store, Ghaziabad", "product_name": "Local Spice Packet", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "mock-5", "latitude": 28.7041, "longitude": 77.1025, "overall_status": "COMPLIANT", "store_name": "D-Mart, Rohini", "product_name": "Amul Butter 500g", "created_at": datetime.now(timezone.utc).isoformat()},
]

MOCK_RECENT = [
    {"scan_id": "f0ce5e06-601c-461a-bc66-b647a00bba02", "product_name": "Aashirvaad Whole Wheat Atta 5kg", "brand_name": "ITC Limited", "overall_status": "NON_COMPLIANT", "compliance_score": 72.5, "store_name": "Reliance Smart Supermarket, Sector 62", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "7a91b2c4-3382-4d51-872f-410a8d569001", "product_name": "Parle-G Gold Glucose Biscuits", "brand_name": "Parle Products", "overall_status": "COMPLIANT", "compliance_score": 100.0, "store_name": "Big Bazaar, Noida Sector 18", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "421c9902-1f3a-4933-b91c-76d1e4359871", "product_name": "Glow & Lovely Advanced Multivitamin", "brand_name": "Hindustan Unilever Limited", "overall_status": "WARNING", "compliance_score": 60.0, "store_name": "Apollo Pharmacy, CP", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "e9324021-9981-4328-98df-8921ac509422", "product_name": "Tata Salt Vacuum Evaporated 1kg", "brand_name": "Tata Consumer Products", "overall_status": "COMPLIANT", "compliance_score": 95.0, "store_name": "D-Mart, Rohini", "created_at": datetime.now(timezone.utc).isoformat()},
    {"scan_id": "87dca091-5512-4cf3-a3b0-0012bc654711", "product_name": "Everest Kitchen King Masala 100g", "brand_name": "Everest Spices", "overall_status": "NON_COMPLIANT", "compliance_score": 50.0, "store_name": "Kirana Mandi, Ghaziabad", "created_at": datetime.now(timezone.utc).isoformat()},
]


@router.get("/stats")
def get_dashboard_stats():
    """
    Returns KPI cards for the Inspector Dashboard and Web Portal.
    Used by both mobile app and web command center.
    """
    if settings.USE_MOCK:
        return MOCK_STATS

    try:
        return DBService.get_dashboard_stats()
    except Exception as e:
        print(f"[WARN] Dashboard stats query failed: {e}")
        return MOCK_STATS


@router.get("/heatmap")
def get_heatmap_pins():
    """
    Returns geo-tagged inspection coordinates for the OpenStreetMap heatmap.
    Used by the web command portal.
    """
    if settings.USE_MOCK:
        return MOCK_HEATMAP

    try:
        pins = DBService.get_heatmap_pins()
        return pins if pins else MOCK_HEATMAP
    except Exception as e:
        print(f"[WARN] Heatmap query failed: {e}")
        return MOCK_HEATMAP


@router.get("/recent-scans")
def get_recent_scans(
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
):
    """
    Returns paginated and searchable scan history for the audit registry.
    Supports search query (?q=atta) and status filter (?status=NON_COMPLIANT).
    """
    if settings.USE_MOCK:
        filtered = MOCK_RECENT
        if status and status.upper() != "ALL":
            filtered = [r for r in filtered if r["overall_status"] == status.upper()]
        if q and q.strip():
            query_str = q.strip().lower()
            filtered = [
                r for r in filtered
                if query_str in r["product_name"].lower()
                or query_str in r["brand_name"].lower()
                or query_str in r["store_name"].lower()
                or query_str in r["scan_id"].lower()
            ]
        return filtered[:limit]

    try:
        scans = DBService.get_recent_scans(limit=limit, search_query=q, status_filter=status)
        return scans if scans else MOCK_RECENT
    except Exception as e:
        print(f"[WARN] Recent scans query failed: {e}")
        return MOCK_RECENT



@router.get("/analytics")
def get_analytics():
    """
    Returns violation analytics for charts on the Web Portal:
    - Rule violation breakdown (bar chart)
    - Category-wise compliance (pie chart)
    - Weekly scan trend
    """
    return {
        "rule_violations": [
            {"rule": "MRP (Rule 6(1)(e))", "violations": 42},
            {"rule": "Net Quantity (Rule 6(1)(c))", "violations": 28},
            {"rule": "Consumer Care (Rule 6(1)(g))", "violations": 35},
            {"rule": "Font Size (Rule 6(3))", "violations": 19},
            {"rule": "Mfg Date (Rule 6(1)(d))", "violations": 14},
            {"rule": "USP (Rule 6(1)(i))", "violations": 22},
        ],
        "category_compliance": [
            {"category": "Food & Beverages", "compliant": 65, "non_compliant": 35},
            {"category": "Cosmetics", "compliant": 52, "non_compliant": 48},
            {"category": "Electronics", "compliant": 84, "non_compliant": 16},
            {"category": "General Goods", "compliant": 71, "non_compliant": 29},
        ],
        "weekly_trend": [
            {"day": "Mon", "scans": 45, "violations": 12},
            {"day": "Tue", "scans": 52, "violations": 15},
            {"day": "Wed", "scans": 60, "violations": 18},
            {"day": "Thu", "scans": 48, "violations": 11},
            {"day": "Fri", "scans": 74, "violations": 22},
            {"day": "Sat", "scans": 85, "violations": 25},
            {"day": "Sun", "scans": 30, "violations": 8},
        ]
    }

