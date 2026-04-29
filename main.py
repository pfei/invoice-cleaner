import csv
import json
import os
import re

import dateparser
import pdfplumber


def clean_amount(amount_str):
    """Converts string amount to a clean float."""
    if not amount_str:
        return None
    try:
        return float(amount_str.replace(",", ".").strip())
    except ValueError:
        return None


def clean_date(date_str):
    """Normalizes date strings to ISO format (YYYY-MM-DD)."""
    if not date_str:
        return None
    dt = dateparser.parse(date_str)
    return dt.strftime("%Y-%m-%d") if dt else None


def extract_free(text):
    """Extracts and normalizes Free SAS invoice data."""
    amount_pat = r"Somme à payer\s+([\d,.]+)\s+€ TTC"
    date_pat = r"du (\d{2} \w+ \d{4})"

    amount_match = re.search(amount_pat, text)
    date_match = re.search(date_pat, text)

    return {
        "amount": clean_amount(amount_match.group(1)) if amount_match else None,
        "date": clean_date(date_match.group(1)) if date_match else None,
        "provider": "Free",
    }


def extract_aws(text):
    """Extracts and normalizes AWS invoice data."""
    amount_pat = r"Total for this invoice.*?\$([\d.]+)"
    date_pat = r"Invoice Date:.*?([a-zA-Z]+\s+\d{1,2}\s*,\s+\d{4})"

    amount_match = re.search(amount_pat, text, re.DOTALL | re.IGNORECASE)
    date_match = re.search(date_pat, text, re.DOTALL | re.IGNORECASE)

    return {
        "amount": clean_amount(amount_match.group(1)) if amount_match else None,
        "date": clean_date(date_match.group(1)) if date_match else None,
        "provider": "AWS",
    }


def save_results(results, output_dir="output", base_filename="invoices_report"):
    """Serializes extraction results to JSON and CSV formats."""
    if not results:
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_path = os.path.join(output_dir, f"{base_filename}.json")
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    keys = results[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


def main():
    input_dir = "examples"
    output_dir = "output"
    results = []

    if not os.path.exists(input_dir):
        return

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_dir, filename)

            try:
                with pdfplumber.open(file_path) as pdf:
                    full_text = "\n".join(
                        [p.extract_text() for p in pdf.pages if p.extract_text()]
                    )

                if "Free SAS" in full_text or "Somme à payer" in full_text:
                    data = extract_free(full_text)
                elif "Amazon Web Services" in full_text or "AWS" in full_text:
                    data = extract_aws(full_text)
                else:
                    data = {"amount": None, "date": None, "provider": "Unknown"}

                data["file_source"] = filename
                results.append(data)

            except Exception:
                continue

    save_results(results, output_dir=output_dir)


if __name__ == "__main__":
    main()
