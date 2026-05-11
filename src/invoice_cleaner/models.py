from dataclasses import dataclass
from typing import Optional


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
