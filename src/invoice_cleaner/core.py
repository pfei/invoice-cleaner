import logging
import os

import pdfplumber
from src.invoice_cleaner.models import InvoiceRecord

from src.invoice_cleaner.providers.aws import extract_aws
from src.invoice_cleaner.providers.free import extract_free
from src.invoice_cleaner.providers.generic import extract_generic
from src.invoice_cleaner.providers.ovh import extract_ovh

logger = logging.getLogger(__name__)

_EXTRACTORS = {
    "Free": extract_free,
    "AWS": extract_aws,
    "OVH": extract_ovh,
}

_PREVIEW_LENGTH = 200


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


def parse_invoice(file_path: str) -> InvoiceRecord:
    """
    Opens a PDF invoice, detects its provider, and extracts structured data.

    For unknown providers, falls back to generic pattern matching and logs
    a preview of the extracted text to help diagnose missing extractors.

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
        logger.warning("No extractor for provider 'Unknown' — file: %s", filename)
        logger.debug(
            "Text preview for '%s': %s",
            filename,
            full_text[:_PREVIEW_LENGTH].replace("\n", " "),
        )
        amount, date = extract_generic(full_text)
        if amount is None and date is None:
            logger.warning(
                "Generic fallback also failed for '%s' — manual extractor may be needed",
                filename,
            )
        else:
            logger.info(
                "Generic fallback partial result for '%s': amount=%s date=%s",
                filename,
                amount,
                date,
            )

    return InvoiceRecord(
        file_source=filename,
        provider=provider,
        amount=amount,
        date=date,
    )
