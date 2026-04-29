import re

import pdfplumber


def extract_amount(text):
    """
    Search for the total amount after the 'Somme à payer' label.
    Pattern: Matches decimal numbers followed by '€ TTC'.
    """
    #
    pattern = r"Somme à payer\s+([\d.]+)\s+€ TTC"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def extract_date(text):
    """
    Search for the invoice date starting with 'du'.
    Pattern: Matches 'DD Month YYYY'.
    """
    #
    pattern = r"du (\d{2} \w+ \d{4})"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def main():
    file_path = "examples/free-fiber-invoice.pdf"

    try:
        with pdfplumber.open(file_path) as pdf:
            # Extract text from all pages and merge[cite: 1]
            full_text = "\n".join(
                [page.extract_text() for page in pdf.pages if page.extract_text()]
            )

        # Business logic: extract specific fields
        amount = extract_amount(full_text)
        date = extract_date(full_text)

        # Simple output
        print(f"Amount: {amount}")
        print(f"Date: {date}")

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
