import re

import pdfplumber


def extract_free(text):
    """
    Extracts data from Free SAS invoices.
    """
    amount_pat = r"Somme à payer\s+([\d.]+)\s+€ TTC"
    date_pat = r"du (\d{2} \w+ \d{4})"

    amount = re.search(amount_pat, text)
    date = re.search(date_pat, text)

    return {
        "amount": amount.group(1) if amount else None,
        "date": date.group(1) if date else None,
    }


def extract_aws(text):
    """
    Extracts data from AWS invoices using flexible whitespace handling.
    Note: AWS PDF extraction often includes a space before the comma in the date.
    """
    # Matches 'Total for this invoice' followed by anything until '$' and digits
    amount_pat = r"Total for this invoice.*?\$([\d.]+)"

    # Matches 'Invoice Date:' followed by 'Month Day , Year' (handles floating comma)
    date_pat = r"Invoice Date:.*?([a-zA-Z]+\s+\d{1,2}\s*,\s+\d{4})"

    amount = re.search(amount_pat, text, re.DOTALL | re.IGNORECASE)
    date = re.search(date_pat, text, re.DOTALL | re.IGNORECASE)

    return {
        "amount": amount.group(1).strip() if amount else None,
        "date": date.group(1).strip() if date else None,
    }


def main():
    file_paths = [
        "examples/free-fiber-invoice.pdf",
        "examples/AmazonWebServices-invoice.pdf",
    ]

    for file_path in file_paths:
        print(f"--- Processing: {file_path} ---")
        try:
            with pdfplumber.open(file_path) as pdf:
                full_text = "\n".join(
                    [page.extract_text() for page in pdf.pages if page.extract_text()]
                )

            if "Free SAS" in full_text or "Somme à payer" in full_text:
                data = extract_free(full_text)
            elif "Amazon Web Services" in full_text or "AWS" in full_text:
                data = extract_aws(full_text)
            else:
                data = {"amount": None, "date": None}

            print(f"Amount: {data['amount']}")
            print(f"Date: {data['date']}\n")

        except FileNotFoundError:
            print(f"Error: {file_path} not found.\n")
        except Exception as e:
            print(f"An unexpected error occurred: {e}\n")


if __name__ == "__main__":
    main()
