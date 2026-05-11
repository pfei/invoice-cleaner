import dateparser


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
