import re
from typing import Optional

from src.invoice_cleaner.utils import clean_amount, clean_date


# Generic patterns that work across many invoice formats
_AMOUNT_PATTERNS = [
    r"(?:total|amount|montant|somme)[^\d]{0,20}([\d]+[.,][\d]{2})\s*[€$£]",
    r"([\d]+[.,][\d]{2})\s*[€$£]",
    r"[€$£]\s*([\d]+[.,][\d]{2})",
]

_DATE_PATTERNS = [
    r"\b(\d{4}-\d{2}-\d{2})\b",                          # ISO: 2024-03-01
    r"\b(\d{2}/\d{2}/\d{4})\b",                          # 01/03/2024
    r"\b(\d{1,2}\s+\w+\s+\d{4})\b",                      # 1 March 2024
    r"\b([a-zA-Z]+\s+\d{1,2},?\s+\d{4})\b",              # March 1, 2024
]


def extract_generic(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Fallback extractor for unknown invoice providers.

    Tries common amount and date patterns without provider-specific assumptions.
    Results are best-effort and may be inaccurate.

    Args:
        text: Full text content of the PDF.

    Returns:
        Tuple of (amount, iso_date). Either or both may be None.
    """
    amount = _extract_amount(text)
    date = _extract_date(text)
    return amount, date


def _extract_amount(text: str) -> Optional[float]:
    for pattern in _AMOUNT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return clean_amount(match.group(1))
    return None


def _extract_date(text: str) -> Optional[str]:
    for pattern in _DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result = clean_date(match.group(1))
            if result:
                return result
    return None
