import csv
import json
import os
import re

import pdfplumber


def extract_free(text):
    """
    Extracts invoice data for Free SAS (French ISP).

    Args:
        text (str): Raw text extracted from the PDF.
    Returns:
        dict: Extracted amount, date, and provider label.
    """
    amount_pat = r"Somme à payer\s+([\d.]+)\s+€ TTC"
    date_pat = r"du (\d{2} \w+ \d{4})"

    amount = re.search(amount_pat, text)
    date = re.search(date_pat, text)

    return {
        "amount": amount.group(1) if amount else None,
        "date": date.group(1) if date else None,
        "provider": "Free",
    }


def extract_aws(text):
    """
    Extracts invoice data for Amazon Web Services.
    Handles specific PDF artifacts like floating commas and multiline breaks.
    """
    amount_pat = r"Total for this invoice.*?\$([\d.]+)"
    date_pat = r"Invoice Date:.*?([a-zA-Z]+\s+\d{1,2}\s*,\s+\d{4})"

    amount = re.search(amount_pat, text, re.DOTALL | re.IGNORECASE)
    date = re.search(date_pat, text, re.DOTALL | re.IGNORECASE)

    return {
        "amount": amount.group(1).strip() if amount else None,
        "date": date.group(1).strip() if date else None,
        "provider": "AWS",
    }


def save_results(results, output_dir="output", base_filename="invoices_report"):
    """
    Serializes extraction results to JSON and CSV formats in a specific directory.

    Args:
        results (list): List of dictionaries containing invoice data.
        output_dir (str): Directory where files will be saved.
        base_filename (str): Base name for the output files.
    """
    if not results:
        print("No data to export.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    json_path = os.path.join(output_dir, f"{base_filename}.json")
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")

    # JSON serialization
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    # CSV serialization
    keys = results[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(
        f"Reports successfully generated in '{output_dir}':\n - {json_path}\n - {csv_path}"
    )


def main():
    """
    Main execution loop. Orchestrates file discovery, extraction,
    and data exportation.
    """
    input_dir = "examples"
    output_dir = "output"
    results = []

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    # Iterate through PDF files in the target directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_dir, filename)

            try:
                with pdfplumber.open(file_path) as pdf:
                    # Aggregate text content from all pages
                    full_text = "\n".join(
                        [p.extract_text() for p in pdf.pages if p.extract_text()]
                    )

                # Route to the appropriate extractor based on content keywords
                if "Free SAS" in full_text or "Somme à payer" in full_text:
                    data = extract_free(full_text)
                elif "Amazon Web Services" in full_text or "AWS" in full_text:
                    data = extract_aws(full_text)
                else:
                    data = {"amount": None, "date": None, "provider": "Unknown"}

                # Metadata attachment and integrity check
                data["file_source"] = filename
                results.append(data)

                print(f"Processed: {filename} [{data['provider']}]")

            except Exception as e:
                print(f"Critical error processing {filename}: {e}")

    save_results(results, output_dir=output_dir)


if __name__ == "__main__":
    main()
