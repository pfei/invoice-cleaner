"""
invoice-cleaner — Fast-path PDF invoice data extractor.

Extracts structured fields (amount, date, provider) from known invoice formats
using regex-based heuristics. Outputs results as JSON and CSV.
"""

import csv
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Optional

import dateparser
import pdfplumber

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class InvoiceRecord:
    """Structured representation of an extracted invoice."""

    file_source: str
    provider: str
    amount: Optional[float]
    date: Optional[str]

    @property
    def is_valid(self) -> bool:
        """Returns True if all required fields were successfully extracted."""
        return self.amount is not None and self.date is not None


# ---------------------------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------------------------


def clean_amount(amount_str: str) -> Optional[float]:
    """
    Converts a raw string amount to a float.

    Handles both comma and dot decimal separators.

    Args:
        amount_str: Raw amount string (e.g. "29,99" or "1234.56").

    Returns:
        Parsed float, or None if conversion fails.
    """
    if not amount_str:
        return None
    try:
        return float(amount_str.replace(",", ".").strip())
    except ValueError:
        logger.debug("Could not parse amount: %r", amount_str)
        return None


def clean_date(date_str: str) -> Optional[str]:
    """
    Normalizes a date string to ISO 8601 format (YYYY-MM-DD).

    Relies on dateparser for locale-agnostic parsing.

    Args:
        date_str: Raw date string in any supported locale.

    Returns:
        ISO-formatted date string, or None if parsing fails.
    """
    if not date_str:
        return None
    dt = dateparser.parse(date_str)
    if not dt:
        logger.debug("Could not parse date: %r", date_str)
        return None
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Provider extractors
# ---------------------------------------------------------------------------


def extract_free(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Extracts amount and date from a Free SAS invoice.

    Expected patterns:
      - Amount: "Somme à payer  29,99 € TTC"
      - Date:   "du 15 janvier 2024"

    Args:
        text: Full text content of the PDF.

    Returns:
        Tuple of (amount, iso_date).
    """
    amount_match = re.search(r"Somme à payer\s+([\d,.]+)\s+€ TTC", text)
    date_match = re.search(r"du (\d{2} \w+ \d{4})", text)

    return (
        clean_amount(amount_match.group(1)) if amount_match else None,
        clean_date(date_match.group(1)) if date_match else None,
    )


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
    amount_match = re.search(
        r"Total for this invoice.*?\$([\d.]+)", text, re.DOTALL | re.IGNORECASE
    )
    date_match = re.search(
        r"Invoice Date:.*?([a-zA-Z]+\s+\d{1,2}\s*,\s+\d{4})",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    return (
        clean_amount(amount_match.group(1)) if amount_match else None,
        clean_date(date_match.group(1)) if date_match else None,
    )


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


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


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
        logger.warning("No extractor for provider '%s' — file: %s", provider, filename)

    return InvoiceRecord(
        file_source=filename,
        provider=provider,
        amount=amount,
        date=date,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_results(
    records: list[InvoiceRecord],
    output_dir: str = "output",
    base_filename: str = "invoices_report",
) -> None:
    """
    Serializes a list of InvoiceRecord objects to JSON and CSV.

    Args:
        records:       List of extracted invoice records.
        output_dir:    Target directory (created if it does not exist).
        base_filename: Base name for output files (no extension).
    """
    if not records:
        logger.info("No records to save.")
        return

    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, f"{base_filename}.json")
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")

    dicts = [asdict(r) for r in records]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dicts, f, indent=4, ensure_ascii=False)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
        writer.writeheader()
        writer.writerows(dicts)

    logger.info("Results saved → %s | %s", json_path, csv_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """
    Discovers PDF invoices in the input directory, parses each one,
    and writes consolidated results to the output directory.
    """
    input_dir = "examples"
    output_dir = "output"

    if not os.path.isdir(input_dir):
        logger.error("Input directory '%s' not found.", input_dir)
        sys.exit(1)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logger.warning("No PDF files found in '%s'.", input_dir)
        return

    logger.info("Found %d PDF invoice(s) to process.", len(pdf_files))

    records: list[InvoiceRecord] = []
    success = failed = 0

    for filename in sorted(pdf_files):
        file_path = os.path.join(input_dir, filename)
        try:
            record = parse_invoice(file_path)
            records.append(record)
            if record.is_valid:
                success += 1
                logger.info(
                    "✓  %-40s  provider=%-8s  amount=%-10s  date=%s",
                    filename,
                    record.provider,
                    record.amount,
                    record.date,
                )
            else:
                failed += 1
                logger.warning(
                    "⚠  %-40s  provider=%-8s  — incomplete extraction",
                    filename,
                    record.provider,
                )
        except RuntimeError as exc:
            failed += 1
            logger.error("✗  %s", exc)

    save_results(records, output_dir=output_dir)

    print(f"\nProcessed : {len(pdf_files)}")
    print(f"Success   : {success}")
    print(f"Failed    : {failed}")


if __name__ == "__main__":
    main()
