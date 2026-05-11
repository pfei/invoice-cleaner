import logging
import os

import pdfplumber
from src.invoice_cleaner.models import InvoiceRecord

from src.invoice_cleaner.providers.aws import extract_aws
from src.invoice_cleaner.providers.free import extract_free
from src.invoice_cleaner.providers.ovh import extract_ovh

logger = logging.getLogger(__name__)


def detect_provider(text: str) -> str:
    """
    Identifies the invoice provider based on known textual signatures.

    Args:
        text: Full text content of the PDF.

    Returns:
        Provider name string: "Free", "AWS", "OVH", or "Unknown".
    """
    if "Free SAS" in text or "Somme à payer" in text:
        return "Free"

    if "Amazon Web Services" in text or "AWS" in text:
        return "AWS"

    if "OVH" in text or "Date de facturation" in text:
        return "OVH"

    return "Unknown"


_EXTRACTORS = {
    "Free": extract_free,
    "AWS": extract_aws,
    "OVH": extract_ovh,
}


def parse_invoice(file_path: str) -> InvoiceRecord:
    """
    Opens a PDF invoice, detects its provider, and extracts structured data.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        An InvoiceRecord with extracted fields (some may be None on failure).

    Raises:
        RuntimeError: If the PDF cannot be opened or read.
    """
    filename = os.path.basename(file_path)

    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )

    except Exception as exc:
        raise RuntimeError(f"Failed to read PDF '{filename}': {exc}") from exc

    provider = detect_provider(full_text)
    extractor = _EXTRACTORS.get(provider)

    if extractor:
        amount, date = extractor(full_text)

    else:
        amount, date = None, None
        logger.warning(
            "No extractor for provider '%s' — file: %s",
            provider,
            filename,
        )

    return InvoiceRecord(
        file_source=filename,
        provider=provider,
        amount=amount,
        date=date,
    )
