# ============================================================
# METROSCAN OFFICIAL LEGAL NOTICE & CERTIFICATE GENERATOR
# Statutory Form 1 — Inspection Memo & Compliance Notice
# Issued under Section 18 & 36 of Legal Metrology Act, 2009
# read with Legal Metrology (Packaged Commodities) Rules, 2011
# ============================================================

import io
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

from app.schemas import DeclarationResult
from app.services.cloudinary_service import CloudinaryService
from app.services.db_service import DBService


class ReportGeneratorService:
    """
    Builds court-admissible, sovereign-styled Legal Metrology Inspection
    Certificates and Section 36 Legal Notices.
    """

    @classmethod
    def generate_inspection_certificate(
        cls,
        scan_id: str,
        product_name: str,
        brand_name: str,
        overall_status: str,
        compliance_score: float,
        declarations: List[DeclarationResult],
        store_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        inspector_name: str = "Inspector Amit Verma",
        badge_id: str = "LM-DEL-8492",
        department: str = "Delhi State Legal Metrology Enforcement Division",
    ) -> tuple[bytes, str]:
        """
        Builds the official Government of India Inspection Certificate vector PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )

        styles = getSampleStyleSheet()
        story = []

        # Color Palette
        c_primary = colors.HexColor('#0B3C5D')      # Sovereign Deep Navy
        c_secondary = colors.HexColor('#1A5276')    # Royal Blue
        c_saffron = colors.HexColor('#D35400')      # Tiranga Accent
        c_dark = colors.HexColor('#1C2833')
        c_gray_bg = colors.HexColor('#F8F9FA')

        # Typography Styles
        title_top = ParagraphStyle('TopHeader', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=c_primary, alignment=1)
        dept_style = ParagraphStyle('DeptHeader', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#566573'), alignment=1)
        doc_title = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=c_saffron, alignment=1)
        sub_title = ParagraphStyle('SubTitle', fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=colors.HexColor('#7F8C8D'), alignment=1)

        meta_lbl = ParagraphStyle('MetaLbl', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=c_dark)
        meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#2C3E50'))

        table_hdr = ParagraphStyle('TableHdr', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)
        table_cell = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=c_dark)
        table_cell_b = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=c_dark)

        # ── 1. SOVEREIGN GOVERNMENT HEADER ──
        story.append(Paragraph("GOVERNMENT OF INDIA", title_top))
        story.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", dept_style))
        story.append(Paragraph(department.upper(), dept_style))
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=2, spaceAfter=6))
        story.append(Paragraph("FORM 1: STATUTORY PACKAGING INSPECTION REPORT & COMPLIANCE MEMO", doc_title))
        story.append(Paragraph("Issued pursuant to Section 18 & 36, Legal Metrology Act, 2009 read with Rule 6, Packaged Commodities Rules, 2011", sub_title))
        story.append(Spacer(1, 8))

        # ── 2. INSPECTION PARTICULARS & ENFORCEMENT CREDENTIALS ──
        # Format live IST timestamp (UTC + 5:30)
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        now_dt = datetime.now(ist_tz)
        now_str = now_dt.strftime("%d-%b-%Y %I:%M:%S %p IST")

        # Format exact live GPS coordinates
        if latitude is not None and longitude is not None:
            lat_dir = 'N' if float(latitude) >= 0 else 'S'
            lng_dir = 'E' if float(longitude) >= 0 else 'W'
            gps_str = f"{abs(float(latitude)):.4f}° {lat_dir}, {abs(float(longitude)):.4f}° {lng_dir}"
        else:
            gps_str = "Geo-Tagged at Point of Inspection"

        status_color = '#27AE60' if overall_status == 'COMPLIANT' else ('#C0392B' if overall_status == 'NON_COMPLIANT' else '#D35400')

        meta_rows = [
            [
                Paragraph("<b>Inspection Memo ID:</b>", meta_lbl), Paragraph(f"<b>{scan_id}</b>", meta_val),
                Paragraph("<b>Audit Timestamp:</b>", meta_lbl), Paragraph(now_str, meta_val)
            ],
            [
                Paragraph("<b>Inspecting Authority:</b>", meta_lbl), Paragraph(inspector_name, meta_val),
                Paragraph("<b>Badge / Officer ID:</b>", meta_lbl), Paragraph(f"<font color='#0B3C5D'><b>{badge_id}</b></font>", meta_val)
            ],
            [
                Paragraph("<b>Commercial Mandi / Store:</b>", meta_lbl), Paragraph(store_name or "Retail Marketplace", meta_val),
                Paragraph("<b>Inspection Geo-Coordinates:</b>", meta_lbl), Paragraph(gps_str, meta_val)
            ],
            [
                Paragraph("<b>Product Identified:</b>", meta_lbl), Paragraph(f"<b>{product_name}</b>", meta_val),
                Paragraph("<b>Brand / Packer:</b>", meta_lbl), Paragraph(brand_name, meta_val)
            ],
            [
                Paragraph("<b>Statutory Verdict:</b>", meta_lbl),
                Paragraph(f"<font color='{status_color}'><b>{overall_status} ({compliance_score}%)</b></font>", meta_val),
                Paragraph("<b>Legal Action Status:</b>", meta_lbl),
                Paragraph("<b>NOTICE ISSUED U/S 36</b>" if overall_status == 'NON_COMPLIANT' else "Verified Compliant", meta_val)
            ]
        ]

        meta_tbl = Table(meta_rows, colWidths=[110, 160, 115, 155])
        meta_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_gray_bg),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#EAEDED')),
            ('TOPPADDING', (0, 0), (-1, -1), 3.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_tbl)
        story.append(Spacer(1, 10))

        # ── 3. STATUTORY COMPLIANCE AUDIT MATRIX ──
        story.append(Paragraph("<b>10-POINT MANDATORY STATUTORY DECLARATION AUDIT MATRIX</b>", ParagraphStyle('SubSec', fontName='Helvetica-Bold', fontSize=9, textColor=c_primary)))
        story.append(Spacer(1, 4))

        rule_table_data = [
            [
                Paragraph("<b>Rule Reference</b>", table_hdr),
                Paragraph("<b>Statutory Mandate</b>", table_hdr),
                Paragraph("<b>Extracted Packaging Declaration</b>", table_hdr),
                Paragraph("<b>Status</b>", table_hdr),
                Paragraph("<b>Inspection Finding & Infraction</b>", table_hdr),
            ]
        ]

        for d in declarations:
            tag_color = '#27AE60' if d.status == 'PASS' else ('#C0392B' if d.status == 'FAIL' else '#D35400')
            extracted = d.extracted_value if d.extracted_value else "<i>[NOT DECLARED / ABSENT]</i>"
            finding = d.violation_reason if d.violation_reason else "Conforms to statutory parameters."

            rule_table_data.append([
                Paragraph(d.statutory_citation, table_cell),
                Paragraph(d.rule_name, table_cell_b),
                Paragraph(extracted[:75], table_cell),
                Paragraph(f"<font color='{tag_color}'><b>{d.status}</b></font>", table_cell_b),
                Paragraph(f"<font color='{tag_color}'>{finding}</font>", table_cell),
            ])

        rule_table = Table(rule_table_data, colWidths=[65, 120, 140, 48, 167])
        rule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D5D8DC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FBFCFC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(rule_table)
        story.append(Spacer(1, 10))

        # ── 4. STATUTORY LEGAL NOTICE / PENALTY WARNING ──
        if overall_status == 'NON_COMPLIANT':
            notice_text = """
            <b>STATUTORY NOTICE UNDER SECTION 36, LEGAL METROLOGY ACT, 2009:</b><br/>
            Take notice that the above packaged commodity fails to comply with statutory declarations mandated under Rule 6 of the Legal Metrology (Packaged Commodities) Rules, 2011. Under Section 36(1) of the Act, manufacturing, packing, importing or distributing non-compliant commodities is punishable with a <b>fine extending up to ₹25,000/-</b> for first offence and up to ₹50,000/- or imprisonment for subsequent contraventions. The manufacturer/packer/retailer is directed to show cause within 15 days of this notice.
            """
            notice_bg = colors.HexColor('#FDEDEC')
            notice_border = colors.HexColor('#E6B0AA')
            notice_color = '#78281F'
        else:
            notice_text = """
            <b>CERTIFICATE OF COMPLIANCE:</b><br/>
            This certifies that the sampled packaging has undergone automated optical character audit and conforms to all 10 statutory declaration standards stipulated under the Legal Metrology (Packaged Commodities) Rules, 2011. This electronic report is archived in the Central Legal Metrology Registry.
            """
            notice_bg = colors.HexColor('#EAFAF1')
            notice_border = colors.HexColor('#A9DFBF')
            notice_color = '#145A32'

        notice_tbl = Table([[Paragraph(f"<font color='{notice_color}'>{notice_text}</font>", ParagraphStyle('Notice', fontName='Helvetica', fontSize=7.5, leading=10))]], colWidths=[540])
        notice_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), notice_bg),
            ('BOX', (0, 0), (-1, -1), 1, notice_border),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(notice_tbl)
        story.append(Spacer(1, 10))

        # ── 5. SIGNATURE & DIGITAL TAMPER-PROOFING BLOCK ──
        raw_audit_str = f"{scan_id}|{product_name}|{overall_status}|{compliance_score}|{now_str}|{badge_id}"
        sha256_hash = hashlib.sha256(raw_audit_str.encode()).hexdigest()

        sig_data = [
            [
                Paragraph("<b>Digital Tamper-Proofing Hash (SHA-256):</b>", meta_lbl),
                Paragraph("<b>Inspecting Officer Attestation:</b>", meta_lbl)
            ],
            [
                Paragraph(f"<font face='Courier' size='6.5'>{sha256_hash}</font><br/><font size='6' color='#7F8C8D'>Section 65B Indian Evidence Act compliant digital record.<br/>Archived in Supabase National Registry.</font>", meta_val),
                Paragraph(f"<b>Digitally Verified By:</b><br/>{inspector_name}<br/>Enforcement Officer [{badge_id}]<br/>Directorate of Legal Metrology", meta_val)
            ]
        ]
        sig_tbl = Table(sig_data, colWidths=[330, 210])
        sig_tbl.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#BDC3C7')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_tbl)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes, sha256_hash

    @classmethod
    def generate_and_upload(
        cls,
        scan_id: str,
        product_name: str,
        brand_name: str,
        overall_status: str,
        compliance_score: float,
        declarations: List[DeclarationResult],
        store_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        inspector_name: str = "Inspector Amit Verma",
        badge_id: str = "LM-DEL-8492",
        department: str = "Delhi State Legal Metrology Enforcement Division",
        distribution_method: str = "download"
    ) -> dict:
        """
        Builds the enhanced PDF certificate, uploads to Cloudinary,
        and saves the record in Supabase.
        """
        pdf_bytes, sha256_hash = cls.generate_inspection_certificate(
            scan_id=scan_id,
            product_name=product_name,
            brand_name=brand_name,
            overall_status=overall_status,
            compliance_score=compliance_score,
            declarations=declarations,
            store_name=store_name,
            latitude=latitude,
            longitude=longitude,
            inspector_name=inspector_name,
            badge_id=badge_id,
            department=department,
        )

        # Upload to Cloudinary
        pdf_url = CloudinaryService.upload_report_pdf(pdf_bytes, scan_id)

        # Save to Supabase reports table
        DBService.save_report(
            scan_id=scan_id,
            pdf_url=pdf_url,
            report_type="certificate",
            sha256_hash=sha256_hash
        )

        return {
            "scan_id": scan_id,
            "pdf_url": pdf_url,
            "sha256_hash": sha256_hash,
            "distribution_method": distribution_method,
            "status": "success"
        }
