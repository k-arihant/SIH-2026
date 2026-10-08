# ============================================================
# METROSCAN STATUTORY RULE ENGINE
# Deterministic Compliance Verification under
# Legal Metrology (Packaged Commodities) Rules, 2011
# ============================================================

import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from app.schemas import DeclarationResult


class LegalMetrologyRuleEngine:
    """
    Deterministic rule engine that validates extracted packaging text
    against the 10 mandatory statutory declarations.
    """

    # Valid SI Metric Units for Net Quantity (Rule 6(1)(c))
    VALID_SI_UNITS = [
        r'\bkg\b', r'\bg\b', r'\bmg\b',
        r'\bl\b', r'\bml\b', r'\bcl\b',
        r'\bm\b', r'\bcm\b', r'\bmm\b',
        r'\bsq\s*m\b', r'\bsq\s*cm\b',
        r'\bN\b', r'\bU\b', r'\bunits?\b', r'\bpieces?\b', r'\bpcs\b'
    ]

    # Non-compliant / Deceptive units commonly found
    ILLEGAL_UNITS = [
        (r'\bgms\b', "Use of non-standard abbreviation 'gms' (must be 'g')"),
        (r'\bgrams\b', "Spelling out 'grams' is discouraged; statutory SI unit is 'g'"),
        (r'\bkilos\b', "Use of non-standard colloquial 'kilos' (must be 'kg')"),
        (r'\blitres\b|\bltrs\b|\bltr\b', "Use of non-standard abbreviation (must be 'l' or 'L')"),
        (r'\blbs?\b|\bpounds?\b', "Use of non-metric Imperial unit 'lbs' (prohibited under SIH Legal Metrology Act)"),
        (r'\boz\b|\bounces?\b', "Use of non-metric Imperial unit 'oz' (prohibited)"),
    ]

    # Mandatory MRP Tax Clause variations (Rule 6(1)(e))
    MRP_TAX_CLAUSES = [
        r'inclusive\s+of\s+all\s+taxes',
        r'incl\.?\s+of\s+all\s+taxes',
        r'incl\.?\s+all\s+taxes',
        r'inc\.?\s+all\s+taxes',
        r'all\s+taxes\s+included'
    ]

    # Date regex patterns (Rule 6(1)(d))
    DATE_PATTERNS = [
        r'\b(0[1-9]|1[0-2])[\/\.-](20\d{2}|\d{2})\b',                             # MM/YYYY or MM/YY
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,.-]+(20\d{2}|\d{2})\b', # Month YYYY
        r'\b(20\d{2})[\/\.-](0[1-9]|1[0-2])\b',                                   # YYYY/MM
    ]

    # Email & Phone Regex (Rule 6(1)(g))
    EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    PHONE_REGEX = r'(?:\+91[\-\s]?)?[6-9]\d{9}|1800[\-\s]?\d{3,4}[\-\s]?\d{3,4}'

    @classmethod
    def evaluate(
        cls,
        extracted_data: Dict[str, Optional[str]],
        pdp_area_sq_cm: float = 150.0,
        inspection_date: Optional[datetime] = None,
    ) -> Tuple[str, float, List[DeclarationResult]]:
        """
        Evaluates extracted packaging text against all 10 statutory rules.

        Args:
            extracted_data: Dictionary containing key-value text lines:
                - "manufacturer": raw text
                - "product_name": raw text
                - "net_quantity": raw text
                - "mfg_date": raw text
                - "mrp": raw text
                - "expiry_date": raw text
                - "consumer_care": raw text
                - "country_of_origin": raw text
                - "unit_sale_price": raw text
                - "measured_font_height_mm": float (optional)
            pdp_area_sq_cm: Estimated Principal Display Panel area in cm²
            inspection_date: Timestamp of audit (defaults to current UTC time)

        Returns:
            Tuple of (overall_status, compliance_score, List[DeclarationResult])
        """
        if not inspection_date:
            inspection_date = datetime.now(timezone.utc)

        results: List[DeclarationResult] = []

        # 1. Rule 6(1)(a): Manufacturer / Packer / Importer Details
        results.append(cls._check_manufacturer(extracted_data.get("manufacturer")))

        # 2. Rule 6(1)(b): Generic / Common Name of Commodity
        results.append(cls._check_generic_name(extracted_data.get("product_name")))

        # 3. Rule 6(1)(c): Net Quantity & SI Metric Units
        results.append(cls._check_net_quantity(extracted_data.get("net_quantity")))

        # 4. Rule 6(1)(d): Month and Year of Manufacture / Packing
        results.append(cls._check_mfg_date(extracted_data.get("mfg_date")))

        # 5. Rule 6(1)(e): Maximum Retail Price (MRP) & Tax Inclusivity
        results.append(cls._check_mrp(extracted_data.get("mrp")))

        # 6. Rule 6(1)(f): Best Before / Expiry Date (Time-aware statutory validation)
        results.append(cls._check_expiry_date(
            extracted_data.get("expiry_date"),
            mfg_text=extracted_data.get("mfg_date"),
            inspection_date=inspection_date
        ))

        # 7. Rule 6(1)(g): Consumer Care Contact Details
        results.append(cls._check_consumer_care(extracted_data.get("consumer_care")))

        # 8. Rule 6(1)(h): Country of Origin (Imported goods)
        results.append(cls._check_country_of_origin(extracted_data.get("country_of_origin")))

        # 9. Rule 6(1)(i): Unit Sale Price (USP)
        results.append(cls._check_unit_sale_price(extracted_data.get("unit_sale_price"), extracted_data.get("net_quantity")))

        # 10. Rule 6(3): Minimum Font & Numeral Height
        font_height = None
        if extracted_data.get("measured_font_height_mm"):
            try:
                font_height = float(extracted_data["measured_font_height_mm"])
            except (ValueError, TypeError):
                pass
        results.append(cls._check_font_height(font_height, pdp_area_sq_cm))

        # Calculate Compliance Score (Pass = 10 pts, Warning = 5 pts, Fail = 0 pts)
        total_possible = len(results) * 10
        earned = sum(10 if r.status == "PASS" else (5 if r.status == "WARNING" else 0) for r in results)
        score = round((earned / total_possible) * 100.0, 1)

        # Determine Overall Status
        has_critical_fail = any(r.status == "FAIL" for r in results)
        has_warning = any(r.status == "WARNING" for r in results)

        if not has_critical_fail and not has_warning:
            overall_status = "COMPLIANT"
        elif has_critical_fail:
            overall_status = "NON_COMPLIANT"
        else:
            overall_status = "WARNING"

        return overall_status, score, results

    # ── Rule 6(1)(a) Check ────────────────────────────────────
    @classmethod
    def _check_manufacturer(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_A_MFG"
        rule_name = "Manufacturer / Packer / Importer Details"
        citation = "Rule 6(1)(a)"

        if not text or len(text.strip()) < 8:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.95, violation_reason="Manufacturer name or address is completely missing"
            )

        # Check for address indicators (PIN code, state, city)
        has_pin = bool(re.search(r'\b[1-9][0-9]{5}\b', text))
        has_street = bool(re.search(r'\b(road|rd|street|lane|nagar|industrial|plot|sector|phase|estate)\b', text, re.I))

        if has_pin or has_street:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.96
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.85, violation_reason="Name present but physical address lacks PIN code or street details"
            )

    # ── Rule 6(1)(b) Check ────────────────────────────────────
    @classmethod
    def _check_generic_name(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_B_NAME"
        rule_name = "Generic / Common Name of Commodity"
        citation = "Rule 6(1)(b)"

        if not text or len(text.strip()) < 3:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.92, violation_reason="Common or generic identity of commodity not declared"
            )

        return DeclarationResult(
            rule_code=rule_code, rule_name=rule_name, extracted_value=text,
            is_present=True, status="PASS", statutory_citation=citation,
            confidence_score=0.97
        )

    # ── Rule 6(1)(c) Check ────────────────────────────────────
    @classmethod
    def _check_net_quantity(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_C_NET_QTY"
        rule_name = "Net Quantity in Standard SI Units"
        citation = "Rule 6(1)(c)"

        if not text or len(text.strip()) == 0:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.98, violation_reason="Net quantity declaration is missing from the package"
            )

        # Check for illegal / non-standard units first
        for illegal_pattern, reason in cls.ILLEGAL_UNITS:
            if re.search(illegal_pattern, text, re.I):
                return DeclarationResult(
                    rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                    is_present=True, status="FAIL", statutory_citation=citation,
                    confidence_score=0.96, violation_reason=reason
                )

        # Check for valid standard SI unit
        has_si_unit = any(re.search(pat, text, re.I) for pat in cls.VALID_SI_UNITS)
        has_number = bool(re.search(r'\d+', text))

        if has_si_unit and has_number:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.99
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.88, violation_reason="Net quantity format does not match recognized SI metric standard"
            )

    # ── Rule 6(1)(d) Check ────────────────────────────────────
    @classmethod
    def _check_mfg_date(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_D_MFG_DATE"
        rule_name = "Month & Year of Manufacture / Packing"
        citation = "Rule 6(1)(d)"

        if not text:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.94, violation_reason="Manufacturing or packing date is missing"
            )

        has_valid_date = any(re.search(pat, text, re.I) for pat in cls.DATE_PATTERNS)
        if has_valid_date:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.95
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.82, violation_reason="Date present but lacks clear Month/Year format (Rule 6(1)(d))"
            )

    # ── Rule 6(1)(e) Check ────────────────────────────────────
    @classmethod
    def _check_mrp(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_E_MRP"
        rule_name = "Maximum Retail Price (MRP)"
        citation = "Rule 6(1)(e)"

        if not text:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.96, violation_reason="MRP declaration is completely missing"
            )

        has_price = bool(re.search(r'(?:rs\.?|₹|inr)?\s*[\d,]+(?:\.\d{2})?', text, re.I))
        has_tax_clause = any(re.search(clause, text, re.I) for clause in cls.MRP_TAX_CLAUSES)

        if has_price and has_tax_clause:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.98
            )
        elif has_price and not has_tax_clause:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="FAIL", statutory_citation=citation,
                confidence_score=0.95,
                violation_reason="Price declared but MISSING statutory mandatory clause 'inclusive of all taxes'"
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="FAIL", statutory_citation=citation,
                confidence_score=0.90, violation_reason="Ambiguous or unreadable price declaration"
            )

    @classmethod
    def _parse_month_year(cls, text: str) -> Optional[datetime]:
        """Attempts to extract a calendar date from string for expiry verification."""
        if not text:
            return None
        # Check DD/MM/YYYY or DD-MM-YYYY
        m = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\b', text)
        if m:
            d, mo, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if yr < 100:
                yr += 2000
            try:
                return datetime(yr, mo, min(d, 28), tzinfo=timezone.utc)
            except Exception:
                pass

        # Check MM/YYYY or MM-YYYY
        m = re.search(r'\b(\d{1,2})[\/\-\.](\d{2,4})\b', text)
        if m:
            mo, yr = int(m.group(1)), int(m.group(2))
            if yr < 100:
                yr += 2000
            if 1 <= mo <= 12:
                try:
                    return datetime(yr, mo, 28, tzinfo=timezone.utc)
                except Exception:
                    pass

        # Check Month YYYY (e.g. Aug 2024, August 2026)
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        m = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*[\'"]?(\d{2,4})\b', text, re.I)
        if m:
            mo_str, yr_str = m.group(1).lower()[:3], m.group(2)
            yr = int(yr_str)
            if yr < 100:
                yr += 2000
            mo = months.get(mo_str, 1)
            try:
                return datetime(yr, mo, 28, tzinfo=timezone.utc)
            except Exception:
                pass
        return None

    # ── Rule 6(1)(f) Check ────────────────────────────────────
    @classmethod
    def _check_expiry_date(
        cls,
        text: Optional[str],
        mfg_text: Optional[str] = None,
        inspection_date: Optional[datetime] = None
    ) -> DeclarationResult:
        rule_code = "RULE_6_1_F_EXPIRY"
        rule_name = "Best Before / Expiry Date"
        citation = "Rule 6(1)(f)"

        if not inspection_date:
            inspection_date = datetime.now(timezone.utc)

        if not text:
            # For non-perishables, best-before is optional, marked as PASS with note
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=None,
                is_present=False, status="PASS", statutory_citation=citation,
                confidence_score=0.90, violation_reason="Not applicable if commodity is non-perishable"
            )

        # 1. Check if direct expiry date is declared and already passed
        exp_dt = cls._parse_month_year(text)
        if exp_dt:
            if exp_dt < inspection_date:
                diff_days = (inspection_date - exp_dt).days
                return DeclarationResult(
                    rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                    is_present=True, status="FAIL", statutory_citation=citation,
                    confidence_score=0.98,
                    violation_reason=f"CRITICAL VIOLATION: COMMODITY EXPIRED on {exp_dt.strftime('%b %Y')} ({diff_days} days overdue relative to inspection date {inspection_date.strftime('%d-%b-%Y')}). Sale prohibited under Section 36."
                )
            else:
                return DeclarationResult(
                    rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                    is_present=True, status="PASS", statutory_citation=citation,
                    confidence_score=0.97
                )

        # 2. Check if duration declared (e.g. "Best Before: 6 months from Mfg Date")
        dur_match = re.search(r'\b(\d+)\s*(months?|days?|years?)\b', text, re.I)
        if dur_match and mfg_text:
            qty = int(dur_match.group(1))
            unit = dur_match.group(2).lower()
            mfg_dt = cls._parse_month_year(mfg_text)
            if mfg_dt:
                if 'month' in unit:
                    calc_exp = mfg_dt + timedelta(days=qty * 30)
                elif 'day' in unit:
                    calc_exp = mfg_dt + timedelta(days=qty)
                else:
                    calc_exp = mfg_dt + timedelta(days=qty * 365)

                if calc_exp < inspection_date:
                    diff_days = (inspection_date - calc_exp).days
                    return DeclarationResult(
                        rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                        is_present=True, status="FAIL", statutory_citation=citation,
                        confidence_score=0.96,
                        violation_reason=f"CRITICAL VIOLATION: COMMODITY EXPIRED. Declared shelf life of {qty} {unit} from Mfg Date ({mfg_dt.strftime('%b %Y')}) lapsed on {calc_exp.strftime('%b %Y')} ({diff_days} days overdue)."
                    )
                else:
                    return DeclarationResult(
                        rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                        is_present=True, status="PASS", statutory_citation=citation,
                        confidence_score=0.95
                    )

        has_duration = bool(re.search(r'\b\d+\s*(?:months?|days?|years?)\b', text, re.I))
        has_date = any(re.search(pat, text, re.I) for pat in cls.DATE_PATTERNS)

        if has_duration or has_date:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.95
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.80, violation_reason="Unclear expiry or shelf-life declaration"
            )

    # ── Rule 6(1)(g) Check ────────────────────────────────────
    @classmethod
    def _check_consumer_care(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_G_CONSUMER"
        rule_name = "Consumer Care Contact Details"
        citation = "Rule 6(1)(g)"

        if not text:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.96, violation_reason="Consumer grievance details completely absent"
            )

        has_email = bool(re.search(cls.EMAIL_REGEX, text))
        has_phone = bool(re.search(cls.PHONE_REGEX, text))

        if has_email and has_phone:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.97
            )
        elif has_email and not has_phone:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.91,
                violation_reason="Email declared but statutory customer care telephone number is missing"
            )
        elif has_phone and not has_email:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.91,
                violation_reason="Telephone declared but consumer care email address is missing"
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="FAIL", statutory_citation=citation,
                confidence_score=0.88, violation_reason="Consumer care lacks both valid phone and email contacts"
            )

    # ── Rule 6(1)(h) Check ────────────────────────────────────
    @classmethod
    def _check_country_of_origin(cls, text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_H_ORIGIN"
        rule_name = "Country of Origin"
        citation = "Rule 6(1)(h)"

        # For domestic goods, not explicitly flagged as violation unless imported keywords found
        if not text:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=None,
                is_present=False, status="PASS", statutory_citation=citation,
                confidence_score=0.90, violation_reason=None
            )

        return DeclarationResult(
            rule_code=rule_code, rule_name=rule_name, extracted_value=text,
            is_present=True, status="PASS", statutory_citation=citation,
            confidence_score=0.96
        )

    # ── Rule 6(1)(i) Check ────────────────────────────────────
    @classmethod
    def _check_unit_sale_price(cls, text: Optional[str], net_qty_text: Optional[str]) -> DeclarationResult:
        rule_code = "RULE_6_1_I_USP"
        rule_name = "Unit Sale Price (USP)"
        citation = "Rule 6(1)(i)"

        if not text:
            # Flag warning if net quantity suggests multi-unit or non-standard package
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=None,
                is_present=False, status="FAIL", statutory_citation=citation,
                confidence_score=0.90,
                violation_reason="Unit sale price (e.g. Rs. per g/ml) not declared on package"
            )

        has_usp = bool(re.search(r'(?:per|\/)\s*(?:g|kg|ml|l|unit|piece|100g|100ml)', text, re.I))
        if has_usp:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="PASS", statutory_citation=citation,
                confidence_score=0.95
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=text,
                is_present=True, status="WARNING", statutory_citation=citation,
                confidence_score=0.85, violation_reason="Unit sale price lacks standard denominator format"
            )

    # ── Rule 6(3) Check: Minimum Font Height ──────────────────
    @classmethod
    def _check_font_height(cls, measured_mm: Optional[float], pdp_area_sq_cm: float) -> DeclarationResult:
        rule_code = "RULE_6_3_FONT"
        rule_name = "Minimum Font & Numeral Height"
        citation = "Rule 6(3)"

        # Statutory thresholds according to Rule 6(3) Table:
        # Area <= 100 cm²  -> min 1.0 mm
        # 100 to 500 cm²   -> min 2.0 mm
        # 500 to 2500 cm²  -> min 4.0 mm
        # > 2500 cm²       -> min 6.0 mm
        if pdp_area_sq_cm <= 100.0:
            min_required = 1.0
        elif pdp_area_sq_cm <= 500.0:
            min_required = 2.0
        elif pdp_area_sq_cm <= 2500.0:
            min_required = 4.0
        else:
            min_required = 6.0

        if measured_mm is None:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name, extracted_value=f"Required: >= {min_required} mm",
                is_present=False, status="PASS", statutory_citation=citation,
                confidence_score=0.80, violation_reason="Reference object not present for optical millimeter calibration"
            )

        if measured_mm >= min_required:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name,
                extracted_value=f"{measured_mm:.1f} mm (Min required: {min_required} mm)",
                is_present=True, status="PASS", statutory_citation=citation,
                measured_font_height_mm=measured_mm, confidence_score=0.92
            )
        elif measured_mm >= (min_required * 0.8):
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name,
                extracted_value=f"{measured_mm:.1f} mm (Min required: {min_required} mm)",
                is_present=True, status="WARNING", statutory_citation=citation,
                measured_font_height_mm=measured_mm, confidence_score=0.88,
                violation_reason=f"Measured font height ({measured_mm:.1f} mm) is borderline below {min_required} mm threshold"
            )
        else:
            return DeclarationResult(
                rule_code=rule_code, rule_name=rule_name,
                extracted_value=f"{measured_mm:.1f} mm (Min required: {min_required} mm)",
                is_present=True, status="FAIL", statutory_citation=citation,
                measured_font_height_mm=measured_mm, confidence_score=0.94,
                violation_reason=f"Microscopic text violation: font height ({measured_mm:.1f} mm) strictly violates Rule 6(3) minimum of {min_required} mm"
            )
