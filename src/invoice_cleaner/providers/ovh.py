import re
from typing import Optional

from src.invoice_cleaner.utils import clean_amount, clean_date


def extract_ovh(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Extracts amount and date from an OVH invoice.

    Expected patterns:
      - Amount: "Total TTC : 14,40 €"
      - Date:   "Date de facturation : 01/03/2024"

    Args:
        text: Full text content of the PDF.

    Returns:
        Tuple of (amount, iso_date).
    """
    amount_match = re.search(r"Total TTC\s*[:\-]\s*([\d,.]+)\s*€", text, re.IGNORECASE)
    date_match = re.search(
        r"Date de facturation\s*[:\-]\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE
    )

    return (
        clean_amount(amount_match.group(1)) if amount_match else None,
        clean_date(date_match.group(1)) if date_match else None,
    )
