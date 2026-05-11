import pytest
from src.invoice_cleaner.providers.aws import extract_aws
from src.invoice_cleaner.providers.free import extract_free
from src.invoice_cleaner.providers.ovh import extract_ovh


class TestExtractAws:
    AWS_TEXT = """
    Amazon Web Services
    Invoice Date: August 3, 2014
    Total for this invoice  $4.11
    """

    def test_amount(self):
        amount, _ = extract_aws(self.AWS_TEXT)
        assert amount == 4.11

    def test_date(self):
        _, date = extract_aws(self.AWS_TEXT)
        assert date == "2014-08-03"

    def test_missing_amount(self):
        amount, _ = extract_aws("Invoice Date: August 3, 2014")
        assert amount is None

    def test_missing_date(self):
        _, date = extract_aws("Total for this invoice  $4.11")
        assert date is None

    def test_empty_text(self):
        amount, date = extract_aws("")
        assert amount is None
        assert date is None


class TestExtractFree:
    FREE_TEXT = """
    Free SAS
    Somme à payer 29,99 € TTC
    Période du 02 juillet 2015 au 01 août 2015
    """

    def test_amount(self):
        amount, _ = extract_free(self.FREE_TEXT)
        assert amount == 29.99

    def test_date(self):
        _, date = extract_free(self.FREE_TEXT)
        assert date == "2015-07-02"

    def test_missing_amount(self):
        amount, _ = extract_free("du 02 juillet 2015")
        assert amount is None

    def test_missing_date(self):
        _, date = extract_free("Somme à payer 29,99 € TTC")
        assert date is None

    def test_empty_text(self):
        amount, date = extract_free("")
        assert amount is None
        assert date is None


class TestExtractOvh:
    OVH_TEXT = """
    OVH SAS
    Date de facturation : 01/03/2024
    Total TTC : 14,40 €
    """

    def test_amount(self):
        amount, _ = extract_ovh(self.OVH_TEXT)
        assert amount == 14.40

    def test_date(self):
        _, date = extract_ovh(self.OVH_TEXT)
        assert date is not None

    def test_missing_amount(self):
        amount, _ = extract_ovh("Date de facturation : 01/03/2024")
        assert amount is None

    def test_missing_date(self):
        _, date = extract_ovh("Total TTC : 14,40 €")
        assert date is None

    def test_empty_text(self):
        amount, date = extract_ovh("")
        assert amount is None
        assert date is None
