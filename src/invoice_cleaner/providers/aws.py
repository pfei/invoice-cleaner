import re
from typing import Optional

from src.invoice_cleaner.utils import clean_amount, clean_date


def extract_aws(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Extracts amount and date from an Amazon Web Services invoice.

    Expected patterns:
      - Amount: "Total for this invoice  $123.45"
      - Date:   "Invoice Date: March 1, 2024"

    Args:
        text: Full text content of the PDF.

    Returns:
        Tuple of (amount, iso_date).
    """

    amount_pat = r"Total for this invoice.*?\$([\d.]+)"
    date_pat = r"Invoice Date:.*?([a-zA-Z]+\s+\d{1,2}\s*,\s+\d{4})"

    amount_match = re.search(
        amount_pat,
        text,
        re.DOTALL | re.IGNORECASE,
    )

    date_match = re.search(
        date_pat,
        text,
        re.DOTALL | re.IGNORECASE,
    )

    return (
        clean_amount(amount_match.group(1)) if amount_match else None,
        clean_date(date_match.group(1)) if date_match else None,
    )
