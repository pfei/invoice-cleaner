# Invoice Cleaner

A lightweight Python tool designed to extract structured data (amount, date) from PDF invoices using optimized regex patterns.

## ⚠️ Status

This project is in early development (alpha stage).  
API, structure and extraction rules are subject to change.

## 🎯 Purpose

This project demonstrates a **"Fast-Path" parsing strategy**. Before resorting to complex AI models, `invoice-cleaner` uses high-performance heuristic extraction to process known invoice formats (like Free Telecom) in milliseconds.

## 🛠️ Features

*   **Speed**: Near-instant extraction using `pdfplumber` and `re`.
*   **Robustness**: Handles multi-page PDFs and text sanitization.
*   **Extensibility**: Structured with modular functions to easily add new providers.
*   **Open Data**: Includes sample invoices for immediate testing.

## 📂 Project Structure

.
├── examples/           # Sample PDF invoices for testing
├── main.py             # Core extraction logic
├── LICENSE             # MIT License
└── README.md           # Documentation

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/pierre-feilles/invoice-cleaner.git
cd invoice-cleaner
pip install pdfplumber
```

### 3. Usage
Run the main script to process the default example:

python main.py

## 📊 Performance Logic

The script follows a deterministic extraction flow:
1.  **Layout Analysis**: Extracts raw text while maintaining logical groupings.
2.  **Regex Anchoring**: Locates financial data based on semantic anchors like "Somme à payer".
3.  **Sanitization**: Cleans up formatting artifacts to return pure data (e.g., 29.99).

## 📜 Acknowledgments & License

*   **Data Sources**: Some PDF samples in the `examples/` directory are sourced from the [invoice2data](https://github.com/invoice-x/invoice2data) project (MIT License).
*   **License**: This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed by **Pierre Feilles** (2026).