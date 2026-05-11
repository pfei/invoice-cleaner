# invoice-cleaner

> Extract structured data from PDF invoices — fast, no AI required.

![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-37%20passed-brightgreen)

A lightweight Python tool that parses PDF invoices from known providers (AWS, Free, OVH) and extracts structured fields — provider, amount, date — using regex heuristics. Results are exported as JSON and CSV.

Built as a **"fast-path" alternative to AI-based extraction**: for well-structured invoice formats, regex runs in milliseconds and produces deterministic output.

---

## Output example

```
2026-05-11 [INFO] Found 3 PDF invoice(s) to process.
2026-05-11 [INFO] ✓  AmazonWebServices-invoice.pdf   provider=AWS    amount=4.11   date=2014-08-03
2026-05-11 [INFO] ✓  free-fiber-invoice.pdf           provider=Free   amount=29.99  date=2015-07-02
2026-05-11 [WARNING] ⚠  invoice_Trudy Schmidt_14380.pdf  provider=Unknown — incomplete extraction

Processed : 3  |  Success : 2  |  Failed : 1
```

```json
[
  { "file_source": "AmazonWebServices-invoice.pdf", "provider": "AWS",  "amount": 4.11,  "date": "2014-08-03" },
  { "file_source": "free-fiber-invoice.pdf",        "provider": "Free", "amount": 29.99, "date": "2015-07-02" }
]
```

---

## Features

- **Provider detection** — identifies AWS, Free, OVH from PDF text signatures
- **Regex extraction** — amount and date parsed with targeted patterns per provider
- **Date normalization** — any locale/format → ISO 8601 via `dateparser`
- **Dual export** — JSON and CSV output in one run
- **Extensible** — adding a new provider is one file + one line in the router
- **Tested** — 37 unit tests across utils, core logic, and all provider extractors

---

## Project structure

```
invoice-cleaner/
├── src/invoice_cleaner/
│   ├── core.py          # PDF reading, provider detection, routing
│   ├── models.py        # InvoiceRecord dataclass
│   ├── utils.py         # Amount and date normalization
│   └── providers/
│       ├── aws.py
│       ├── free.py
│       └── ovh.py
├── tests/               # pytest — 37 tests
├── examples/            # Sample PDF invoices
├── main.py              # CLI entry point
└── pyproject.toml
```

---

## Getting started

**Requirements:** Python 3.13+, [Poetry](https://python-poetry.org/)

```bash
git clone https://github.com/pfei/invoice-cleaner.git
cd invoice-cleaner
poetry install
poetry run python main.py
```

Results are written to `output/invoices_report.json` and `output/invoices_report.csv`.

**Run the tests:**

```bash
poetry run pytest tests/ -v
```

---

## Adding a new provider

1. Create `src/invoice_cleaner/providers/stripe.py` with an `extract_stripe(text)` function
2. Add a detection signature in `core.py > detect_provider()`
3. Register it in `core.py > _EXTRACTORS`

---

## License

MIT — see [LICENSE](LICENSE).  
Developed by [Pierre Feilles](https://github.com/pfei) (2026).  
Sample invoices from [invoice2data](https://github.com/invoice-x/invoice2data) (MIT).
