import pytest
from src.invoice_cleaner.utils import clean_amount, clean_date


class TestCleanAmount:
    def test_integer_string(self):
        assert clean_amount("42") == 42.0

    def test_decimal_dot(self):
        assert clean_amount("29.99") == 29.99

    def test_decimal_comma(self):
        assert clean_amount("29,99") == 29.99

    def test_whitespace(self):
        assert clean_amount("  14.40  ") == 14.40

    def test_none_input(self):
        assert clean_amount(None) is None

    def test_empty_string(self):
        assert clean_amount("") is None

    def test_invalid_string(self):
        assert clean_amount("not-a-number") is None


class TestCleanDate:
    def test_iso_date(self):
        assert clean_date("2024-03-01") == "2024-03-01"

    def test_french_date(self):
        assert clean_date("15 janvier 2024") == "2024-01-15"

    def test_english_date(self):
        assert clean_date("March 1, 2024") == "2024-03-01"

    def test_slash_date(self):
        assert clean_date("01/03/2024") is not None  # dateparser resolves it

    def test_none_input(self):
        assert clean_date(None) is None

    def test_empty_string(self):
        assert clean_date("") is None

    def test_invalid_string(self):
        assert clean_date("not-a-date") is None
