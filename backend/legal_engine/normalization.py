"""
Reusable Normalization and Parsing Utilities for Legal Metrology Validation.
Normalizes whitespace, units, currency, dates, phone numbers, and emails.
Preserves original strings alongside normalized values.
"""

import re
from typing import Optional, Tuple, List, Dict, Any

# Standard SI Metric and Count Units under Legal Metrology Rules (Second Schedule)
STANDARD_UNITS = {
    # Weight
    "g": "g",
    "gm": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "mg": "mg",
    "milligram": "mg",
    # Volume
    "ml": "ml",
    "m.l.": "ml",
    "millilitre": "ml",
    "milliliter": "ml",
    "millilitres": "ml",
    "l": "L",
    "litre": "L",
    "liter": "L",
    "litres": "L",
    "kl": "kL",
    # Length / Area
    "cm": "cm",
    "m": "m",
    "metre": "m",
    "meter": "m",
    "mm": "mm",
    "sq cm": "cm²",
    "sq m": "m²",
    # Count / Number
    "unit": "Unit",
    "units": "Unit",
    "u": "Unit",
    "n": "N",
    "piece": "Piece",
    "pieces": "Piece",
    "pcs": "Piece",
    "nos": "N",
}

IMPORT_INDICATORS = [
    "imported by",
    "imported and marketed by",
    "imported & marketed by",
    "importer",
    "country of origin",
    "date of import",
    "month & year of import",
    "product of",
]


def clean_whitespace(text: Optional[str]) -> str:
    """Removes extra internal spaces and strips leading/trailing whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_unit(raw_unit: Optional[str]) -> Optional[str]:
    """Maps a raw unit string to standard Legal Metrology unit symbols."""
    if not raw_unit:
        return None
    cleaned = clean_whitespace(raw_unit).lower().rstrip(".,")
    return STANDARD_UNITS.get(cleaned)


def parse_net_quantity(text: Optional[str]) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """
    Parses a net quantity string.
    Returns: (numeric_value, standardized_unit, normalized_string)
    Example: 'Net Qty: 250 g' -> (250.0, 'g', '250 g')
    """
    if not text:
        return None, None, None

    cleaned = clean_whitespace(text)
    
    # Exclude non-quantity patterns like 'Batch No: 250'
    if re.search(r"\b(?:batch|b\.?\s*no|lot)\b", cleaned, re.IGNORECASE):
        return None, None, None

    # Match numeric portion followed by unit
    pattern = r"(\d+(?:,\d+)?(?:\.\d+)?)\s*([a-zA-Z°²³\.\/]+)"
    match = re.search(pattern, cleaned)
    if not match:
        return None, None, None

    num_str = match.group(1).replace(",", "")
    unit_str = match.group(2).strip()

    try:
        num_val = float(num_str)
    except ValueError:
        return None, None, None

    std_unit = normalize_unit(unit_str)
    if not std_unit:
        return num_val, None, f"{num_val} {unit_str}"

    norm_str = f"{int(num_val) if num_val.is_integer() else num_val} {std_unit}"
    return num_val, std_unit, norm_str


def parse_mrp(text: Optional[str]) -> Tuple[Optional[float], bool, str]:
    """
    Parses MRP declaration.
    Returns: (numeric_amount, has_tax_inclusive_clause, normalized_string)
    """
    if not text:
        return None, False, ""

    cleaned = clean_whitespace(text)
    
    # Check for mandatory tax inclusive clause
    tax_inclusive = bool(re.search(
        r"(?:incl\.?|inclusive)\s*(?:of)?\s*(?:all)?\s*taxes", 
        cleaned, 
        re.IGNORECASE
    ))

    # Match price value (₹, Rs, Rs., Rupees, `)
    price_pattern = r"(?:rs\.?|₹|`|inr|rupees)\s*(\d+(?:,\d+)?(?:\.\d+)?)"
    match = re.search(price_pattern, cleaned, re.IGNORECASE)

    if match:
        val_str = match.group(1).replace(",", "")
        try:
            amount = float(val_str)
            norm_str = f"₹ {amount:.2f}"
            return amount, tax_inclusive, norm_str
        except ValueError:
            pass

    # Fallback to general decimal extraction
    num_match = re.search(r"\b(\d+\.\d{2})\b", cleaned)
    if num_match:
        try:
            amount = float(num_match.group(1))
            return amount, tax_inclusive, f"₹ {amount:.2f}"
        except ValueError:
            pass

    return None, tax_inclusive, cleaned


def parse_dates(text: Optional[str]) -> List[str]:
    """
    Extracts dates matching standard formats:
    - MM/YYYY or MM-YYYY
    - DD/MM/YYYY or DD-MM-YYYY
    - Mon YYYY (e.g. JAN 2026, FEB 2026)
    - MM/YY
    """
    if not text:
        return []

    cleaned = clean_whitespace(text)
    patterns = [
        r"\b(?:0[1-9]|1[0-2])[\/\-](?:20\d{2}|\d{2})\b",  # MM/YYYY or MM/YY
        r"\b(?:0[1-9]|[12]\d|3[01])[\/\-](?:0[1-9]|1[0-2])[\/\-](?:20\d{2}|\d{2})\b",  # DD/MM/YYYY
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.\/\-]+(?:20\d{2}|\d{2})\b",  # Month YYYY
    ]

    found = []
    for pat in patterns:
        matches = re.findall(pat, cleaned, re.IGNORECASE)
        found.extend(matches)

    return list(dict.fromkeys(found))


def parse_phone_numbers(text: Optional[str]) -> List[str]:
    """Extracts telephone numbers, 1800 toll-free numbers, or standard mobile numbers."""
    if not text:
        return []

    cleaned = clean_whitespace(text)
    # 1800 toll free or 10-11 digit numbers with optional dashes/spaces
    patterns = [
        r"\b1800[\s\-]?\d{3}[\s\-]?\d{3,4}\b",
        r"\b0\d{2,4}[\s\-]?\d{6,8}\b",
        r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b",
    ]

    phones = []
    for pat in patterns:
        matches = re.findall(pat, cleaned)
        phones.extend(matches)

    return list(dict.fromkeys(phones))


def parse_emails(text: Optional[str]) -> List[str]:
    """Extracts email addresses."""
    if not text:
        return []

    cleaned = clean_whitespace(text)
    pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    return list(dict.fromkeys(re.findall(pattern, cleaned)))


def is_imported_product(
    mfd_text: Optional[str],
    country_of_origin: Optional[str],
    all_text: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Determines if a product is imported based on manufacturer text and country of origin.
    Returns: (is_imported: bool, reason: str)
    """
    combined = f"{mfd_text or ''} {country_of_origin or ''} {all_text or ''}".lower()

    # Check for foreign country declarations
    if country_of_origin:
        co = clean_whitespace(country_of_origin).lower()
        if co and co != "india" and co != "made in india":
            return True, f"Foreign country of origin declared: '{country_of_origin}'"

    # Check for import indicators
    for indicator in IMPORT_INDICATORS:
        if indicator in combined:
            return True, f"Import declaration detected ('{indicator}')"

    return False, "Domestic product (No import declaration detected)"
