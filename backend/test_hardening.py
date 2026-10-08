# ============================================================
# METROSCAN HARDENING VERIFICATION TEST SUITE
# ============================================================

import sys
import os
from datetime import datetime, timezone

def test_imports():
    print("Testing backend imports...")
    from app.config import settings
    from app.dependencies import get_current_user_optional
    from app.services.email_service import EmailService
    from app.services.rule_engine import LegalMetrologyRuleEngine
    from app.services.db_service import DBService
    from app.routes import scan, dashboard, auth
    print("PASS: All backend modules imported successfully.")


def test_time_aware_expiry():
    print("\nTesting Time-Aware Expiry Verification (Rule 6(1)(f))...")
    from app.services.rule_engine import LegalMetrologyRuleEngine

    # Scenario 1: Expired Commodity (Mfg 2022, Best Before 6 months from Mfg Date)
    expired_data = {
        "manufacturer": "Sample Foods Pvt Ltd, Industrial Area, Sector 5, New Delhi 110020",
        "product_name": "Premium Wheat Cookies",
        "net_quantity": "500 g",
        "mfg_date": "01/2022",
        "mrp": "Rs. 150.00 inclusive of all taxes",
        "expiry_date": "Best Before: 6 months from Mfg Date",
        "consumer_care": "care@samplefoods.in, 1800-111-2222",
        "country_of_origin": None,
        "unit_sale_price": "Rs. 0.30 per g",
        "measured_font_height_mm": 3.0,
    }
    status, score, decls = LegalMetrologyRuleEngine.evaluate(expired_data)
    exp_rule = next(d for d in decls if d.rule_code == "RULE_6_1_F_EXPIRY")

    assert exp_rule.status == "FAIL", f"Expected FAIL for expired product, got {exp_rule.status}"
    assert "CRITICAL VIOLATION: COMMODITY EXPIRED" in exp_rule.violation_reason, f"Unexpected reason: {exp_rule.violation_reason}"
    print(f"PASS: Correctly flagged expired commodity -> Status={exp_rule.status}, Reason: {exp_rule.violation_reason}")

    # Scenario 2: Fresh / Valid Commodity (Mfg 08/2026, Best Before 12 months)
    fresh_data = {
        "manufacturer": "Sample Foods Pvt Ltd, Industrial Area, Sector 5, New Delhi 110020",
        "product_name": "Premium Wheat Cookies",
        "net_quantity": "500 g",
        "mfg_date": "08/2026",
        "mrp": "Rs. 150.00 inclusive of all taxes",
        "expiry_date": "Best Before: 12 months from Mfg Date",
        "consumer_care": "care@samplefoods.in, 1800-111-2222",
        "country_of_origin": None,
        "unit_sale_price": "Rs. 0.30 per g",
        "measured_font_height_mm": 3.0,
    }
    status_fresh, score_fresh, decls_fresh = LegalMetrologyRuleEngine.evaluate(fresh_data)
    fresh_exp_rule = next(d for d in decls_fresh if d.rule_code == "RULE_6_1_F_EXPIRY")
    assert fresh_exp_rule.status == "PASS", f"Expected PASS for fresh product, got {fresh_exp_rule.status}"
    print(f"PASS: Correctly verified fresh commodity -> Status={fresh_exp_rule.status}")


def test_email_service():
    print("\nTesting Email Service & Certificate Dispatch...")
    from app.services.email_service import EmailService

    res = EmailService.send_certificate(
        recipient_email="test.officer@gov.in",
        recipient_name="Inspector Test",
        scan_id="f0ce5e06-601c-461a-bc66-b647a00bba02",
        product_name="Aashirvaad Atta 5kg",
        brand_name="ITC Limited",
        overall_status="NON_COMPLIANT",
        compliance_score=72.5,
        pdf_url="https://res.cloudinary.com/havwndoo/raw/upload/v1788804132/metroscan/reports/report_f0ce5e06-601c-461a-bc66-b647a00bba02",
        sha256_hash="cb2a694ce8e6a1b50a332409d84e6d8e54a79be4551b558ccd7220e49b09d3d1",
        store_name="Reliance Smart",
    )
    assert res["status"] == "success", f"Expected success status, got {res}"
    print(f"PASS: Email dispatch simulation succeeded -> {res['message']} (Sender: {res['sender']})")


def test_dashboard_filtering():
    print("\nTesting Dashboard Search and Filtering...")
    from app.routes.dashboard import get_recent_scans

    # Test search query
    atta_results = get_recent_scans(q="Atta")
    assert len(atta_results) > 0, "Expected at least 1 match for query 'Atta'"
    assert "Atta" in atta_results[0]["product_name"]
    print(f"PASS: Search query ?q=Atta returned {len(atta_results)} matches.")

    # Test status filter
    compliant_results = get_recent_scans(status="COMPLIANT")
    for r in compliant_results:
        assert r["overall_status"] == "COMPLIANT"
    print(f"PASS: Status filter ?status=COMPLIANT returned {len(compliant_results)} compliant records.")


def test_fastapi_app():
    print("\nTesting FastAPI App Endpoints via TestClient...")
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. Health endpoint
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print(f"PASS: GET /health returned 200 OK -> {r.json()}")

    # 2. Web Portal root
    r = client.get("/")
    assert r.status_code == 200, f"Root endpoint failed: {r.status_code}"
    assert "METROSCAN" in r.text
    print("PASS: GET / serves MetroScan web portal with 200 OK.")

    # 3. Auth /me endpoint (anonymous)
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["status"] == "anonymous"
    print(f"PASS: GET /api/v1/auth/me (unauthenticated) returned -> {r.json()['status']}")

    # 4. Auth /me endpoint (with mock inspector token)
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer mock-jwt-token-inspector-active"})
    assert r.status_code == 200
    assert r.json()["role"] == "inspector"
    print(f"PASS: GET /api/v1/auth/me (with inspector bearer token) authenticated -> {r.json()['full_name']} ({r.json()['role']})")

    # 5. Email endpoint
    r = client.post(
        "/api/v1/scan/f0ce5e06-601c-461a-bc66-b647a00bba02/email",
        json={"recipient_email": "officer@delhi.gov.in", "recipient_name": "Shri Sharma"}
    )
    assert r.status_code == 200, f"Email endpoint failed: {r.text}"
    print(f"PASS: POST /api/v1/scan/{{scan_id}}/email returned 200 OK -> {r.json()['status']}")

    # 6. Coordinate validation (-90 to 90)
    # Using an image dummy
    from io import BytesIO
    dummy_img = BytesIO(b"fake image data")
    dummy_img.name = "test.jpg"

    r = client.post(
        "/api/v1/scan/analyze",
        data={"latitude": "120.5", "longitude": "77.0"},
        files={"images": ("test.jpg", dummy_img, "image/jpeg")}
    )
    assert r.status_code == 400, f"Expected 400 for out-of-bounds latitude, got {r.status_code}"
    print(f"PASS: POST /api/v1/scan/analyze rejected out-of-bounds latitude with 400 Bad Request: {r.json()['detail']}")


if __name__ == "__main__":
    try:
        test_imports()
        test_time_aware_expiry()
        test_email_service()
        test_dashboard_filtering()
        test_fastapi_app()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! SYSTEM HARDENING 100% VERIFIED!")
        print("=" * 60)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
