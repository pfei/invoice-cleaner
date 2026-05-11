import pytest
from src.invoice_cleaner.providers.generic import extract_generic


class TestExtractGeneric:
    def test_amount_with_euro_after(self):
        amount, _ = extract_generic("Total : 42,50 €")
        assert amount == 42.50

    def test_amount_with_euro_before(self):
        amount, _ = extract_generic("You owe € 99.99 for services rendered.")
        assert amount == 99.99

    def test_amount_with_total_keyword(self):
        amount, _ = extract_generic("Total amount due: 129,00 €")
        assert amount == 129.00

    def test_amount_with_dollar(self):
        amount, _ = extract_generic("Grand total $4.11")
        assert amount == 4.11

    def test_date_iso(self):
        _, date = extract_generic("Invoice date: 2024-03-01")
        assert date == "2024-03-01"

    def test_date_slash(self):
        _, date = extract_generic("Issued on 01/03/2024")
        assert date is not None

    def test_date_english(self):
        _, date = extract_generic("March 1, 2024")
        assert date == "2024-03-01"

    def test_date_natural(self):
        _, date = extract_generic("1 March 2024")
        assert date == "2024-03-01"

    def test_both_found(self):
        amount, date = extract_generic("Total 29,99 € — 2024-01-15")
        assert amount == 29.99
        assert date == "2024-01-15"

    def test_empty_text(self):
        amount, date = extract_generic("")
        assert amount is None
        assert date is None

    def test_no_match(self):
        amount, date = extract_generic("Nothing useful here at all.")
        assert amount is None
        assert date is None
