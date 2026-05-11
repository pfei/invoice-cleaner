import re
from typing import Optional

from src.invoice_cleaner.utils import clean_amount, clean_date


def extract_free(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Extracts amount and date from a Free SAS invoice.

    Expected patterns:
      - Amount: "Somme à payer 29,99 € TTC"
      - Date:   "du 15 janvier 2024"

    Args:
        text: Full text content of the PDF.

    Returns:
        Tuple of (amount, iso_date).
    """

    amount_pat = r"Somme à payer\s+([\d,.]+)\s+€ TTC"
    date_pat = r"du (\d{2} \w+ \d{4})"

    amount_match = re.search(amount_pat, text)

    date_match = re.search(
        date_pat,
        text,
        re.IGNORECASE,
    )

    return (
        clean_amount(amount_match.group(1)) if amount_match else None,
        clean_date(date_match.group(1)) if date_match else None,
    )
