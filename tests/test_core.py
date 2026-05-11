import pytest
from src.invoice_cleaner.core import detect_provider


class TestDetectProvider:
    def test_free_by_name(self):
        assert detect_provider("Free SAS — votre facture") == "Free"

    def test_free_by_keyword(self):
        assert detect_provider("Somme à payer 29,99 € TTC") == "Free"

    def test_aws_by_full_name(self):
        assert detect_provider("Amazon Web Services invoice") == "AWS"

    def test_aws_by_acronym(self):
        assert detect_provider("AWS — Total for this invoice $4.11") == "AWS"

    def test_ovh_by_name(self):
        assert detect_provider("OVH SAS — Facture") == "OVH"

    def test_ovh_by_keyword(self):
        assert detect_provider("Date de facturation : 01/03/2024") == "OVH"

    def test_unknown(self):
        assert detect_provider("Some random PDF content") == "Unknown"

    def test_empty_string(self):
        assert detect_provider("") == "Unknown"
