from supabase import create_client, Client
from app.config import settings
from datetime import datetime, timezone
from typing import Optional

# Initialize Supabase client
_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """Lazy-initialize Supabase client."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase


class DBService:
    """All database operations against Supabase PostgreSQL."""

    @staticmethod
    def get_supabase() -> Client:
        return get_supabase()

    # ── Profiles ──────────────────────────────────────────────

    @staticmethod
    def get_profile(user_id: str) -> dict | None:
        sb = get_supabase()
        result = sb.table("profiles").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None

    # ── Products ──────────────────────────────────────────────

    @staticmethod
    def upsert_product(product_name: str, brand_name: str, barcode: str = None, category: str = "general") -> dict:
        sb = get_supabase()
        data = {
            "product_name": product_name,
            "brand_name": brand_name,
            "category": category,
        }
        if barcode:
            data["barcode"] = barcode
        result = sb.table("products").upsert(data, on_conflict="barcode" if barcode else "").execute()
        return result.data[0] if result.data else data

    # ── Scans ─────────────────────────────────────────────────

    @staticmethod
    def create_scan(
        scan_id: str,
        user_id: Optional[str],
        product_id: Optional[str],
        store_name: Optional[str],
        latitude: Optional[float],
        longitude: Optional[float],
        overall_status: str,
        compliance_score: float,
        raw_text: str = "",
        notes: str = "",
    ) -> dict:
        sb = get_supabase()
        data = {
            "id": scan_id,
            "overall_status": overall_status,
            "compliance_score": compliance_score,
            "raw_text": raw_text,
            "notes": notes,
        }
        if user_id:
            data["user_id"] = user_id
        if product_id:
            data["product_id"] = product_id
        if store_name:
            data["store_name"] = store_name
        if latitude is not None:
            data["latitude"] = latitude
        if longitude is not None:
            data["longitude"] = longitude

        result = sb.table("scans").insert(data).execute()
        return result.data[0] if result.data else data

    # ── Scan Images ───────────────────────────────────────────

    @staticmethod
    def save_scan_image(scan_id: str, image_url: str, annotated_url: str = None, panel_type: str = "front") -> dict:
        sb = get_supabase()
        data = {
            "scan_id": scan_id,
            "image_url": image_url,
            "panel_type": panel_type,
        }
        if annotated_url:
            data["annotated_url"] = annotated_url
        result = sb.table("scan_images").insert(data).execute()
        return result.data[0] if result.data else data

    # ── Declarations ──────────────────────────────────────────

    @staticmethod
    def save_declarations(scan_id: str, declarations: list[dict]) -> list:
        sb = get_supabase()
        rows = []
        for d in declarations:
            rows.append({
                "scan_id": scan_id,
                "rule_code": d["rule_code"],
                "rule_name": d["rule_name"],
                "extracted_value": d.get("extracted_value"),
                "is_present": d.get("is_present", False),
                "status": d.get("status", "FAIL"),
                "measured_font_height_mm": d.get("measured_font_height_mm"),
                "confidence_score": d.get("confidence_score", 0.0),
                "violation_reason": d.get("violation_reason"),
            })
        result = sb.table("declarations").insert(rows).execute()
        return result.data if result.data else rows

    # ── Reports ───────────────────────────────────────────────

    @staticmethod
    def save_report(scan_id: str, pdf_url: str, report_type: str = "certificate", sha256_hash: str = "") -> dict:
        sb = get_supabase()
        data = {
            "scan_id": scan_id,
            "report_type": report_type,
            "pdf_url": pdf_url,
            "sha256_hash": sha256_hash,
        }
        result = sb.table("reports").insert(data).execute()
        return result.data[0] if result.data else data

    # ── Dashboard Queries ─────────────────────────────────────

    @staticmethod
    def get_dashboard_stats() -> dict:
        sb = get_supabase()

        # Total scans
        total = sb.table("scans").select("id", count="exact").execute()
        total_count = total.count or 0

        # Today's scans
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today = sb.table("scans").select("id", count="exact").gte("created_at", f"{today_str}T00:00:00Z").execute()
        today_count = today.count or 0

        # Violations
        violations = sb.table("scans").select("id", count="exact").eq("overall_status", "NON_COMPLIANT").execute()
        violation_count = violations.count or 0

        # Compliance rate
        compliance_rate = ((total_count - violation_count) / total_count * 100) if total_count > 0 else 100.0

        return {
            "total_scans": total_count,
            "today_scans": today_count,
            "violations_detected": violation_count,
            "compliance_rate": round(compliance_rate, 1),
            "pending_notices": violation_count,  # simplified for hackathon
        }

    @staticmethod
    def get_heatmap_pins() -> list:
        sb = get_supabase()
        result = (
            sb.table("scans")
            .select("id, latitude, longitude, overall_status, store_name, created_at")
            .not_.is_("latitude", "null")
            .order("created_at", desc=True)
            .limit(200)
            .execute()
        )
        return result.data or []

    @staticmethod
    def get_recent_scans(
        limit: int = 50,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> list:
        sb = get_supabase()
        try:
            query = sb.table("scans").select(
                "id, overall_status, compliance_score, store_name, created_at, product_id, latitude, longitude"
            )

            if status_filter and status_filter.upper() in ("COMPLIANT", "NON_COMPLIANT", "WARNING"):
                query = query.eq("overall_status", status_filter.upper())

            if search_query and search_query.strip():
                # Filter by store name or id
                query = query.ilike("store_name", f"%{search_query.strip()}%")

            result = query.order("created_at", desc=True).limit(limit).execute()
            rows = result.data or []

            # Enrich rows with product name and brand if available
            enriched = []
            for r in rows:
                p_name = "Packaged Commodity"
                b_name = "Inspected FMCG Brand"
                if r.get("product_id"):
                    try:
                        p_res = sb.table("products").select("product_name, brand_name").eq("id", r["product_id"]).execute()
                        if p_res.data:
                            p_name = p_res.data[0].get("product_name", p_name)
                            b_name = p_res.data[0].get("brand_name", b_name)
                    except Exception:
                        pass
                
                enriched.append({
                    "scan_id": r["id"],
                    "product_name": p_name,
                    "brand_name": b_name,
                    "overall_status": r.get("overall_status", "WARNING"),
                    "compliance_score": float(r.get("compliance_score") or 0.0),
                    "store_name": r.get("store_name") or "Retail Mandi",
                    "latitude": r.get("latitude"),
                    "longitude": r.get("longitude"),
                    "created_at": r.get("created_at"),
                })
            return enriched
        except Exception as e:
            print(f"[WARN] Error in get_recent_scans: {e}")
            return []

    @staticmethod
    def get_scan_full(scan_id: str) -> dict | None:
        """
        Retrieves complete scan audit dossier:
        - metadata
        - all declaration rule checks
        - raw and annotated images
        - generated PDF certificate URL & SHA256 hash
        """
        sb = get_supabase()
        try:
            scan_res = sb.table("scans").select("*").eq("id", scan_id).execute()
            if not scan_res.data:
                return None
            s = scan_res.data[0]

            decl_res = sb.table("declarations").select("*").eq("scan_id", scan_id).execute()
            img_res = sb.table("scan_images").select("*").eq("scan_id", scan_id).execute()
            rep_res = sb.table("reports").select("*").eq("scan_id", scan_id).execute()

            pdf_url = rep_res.data[0]["pdf_url"] if rep_res.data and rep_res.data[0].get("pdf_url") else None
            sha256 = rep_res.data[0].get("sha256_hash") if rep_res.data else None

            images = [img["image_url"] for img in (img_res.data or []) if img.get("image_url")]
            annotated = [img["annotated_url"] for img in (img_res.data or []) if img.get("annotated_url")]

            return {
                "scan_id": s["id"],
                "overall_status": s.get("overall_status"),
                "compliance_score": float(s.get("compliance_score") or 0.0),
                "store_name": s.get("store_name"),
                "latitude": s.get("latitude"),
                "longitude": s.get("longitude"),
                "created_at": s.get("created_at"),
                "declarations": decl_res.data or [],
                "image_urls": images,
                "annotated_image_urls": annotated,
                "pdf_url": pdf_url,
                "sha256_hash": sha256,
            }
        except Exception as e:
            print(f"[WARN] Error fetching full scan dossier: {e}")
            return None

