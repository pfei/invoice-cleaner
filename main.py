"""
invoice-cleaner — Fast-path PDF invoice data extractor.

Extracts structured fields (amount, date, provider) from known invoice formats
using regex-based heuristics. Outputs results as JSON and CSV.

Usage:
    poetry run python main.py
    poetry run python main.py --input /path/to/invoices/
    poetry run python main.py --input /path/to/invoices/ --output /path/to/results/
    poetry run python main.py --log-level DEBUG
"""

import argparse
import csv
import json
import logging
import os
import sys
from dataclasses import asdict

from src.invoice_cleaner.core import parse_invoice
from src.invoice_cleaner.models import InvoiceRecord


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_results(
    records: list[InvoiceRecord],
    output_dir: str = "output",
    base_filename: str = "invoices_report",
) -> None:
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
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract structured data from PDF invoices.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python main.py
  python main.py --input /path/to/invoices/
  python main.py --input /path/to/invoices/ --output /path/to/results/
  python main.py --log-level DEBUG
        """,
    )
    parser.add_argument(
        "--input",
        default="examples",
        metavar="DIR",
        help="Directory containing PDF invoices (default: examples/)",
    )
    parser.add_argument(
        "--output",
        default="output",
        metavar="DIR",
        help="Directory for JSON/CSV results (default: output/)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        metavar="LEVEL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    input_dir = args.input
    output_dir = args.output

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
