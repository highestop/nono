---
name: convert-tesla-charging-xml-to-pdf
description: Convert official Tesla charging invoice XML with the EInvoice structure into a Chinese PDF using the saved A4 layout, with buyer and seller details, itemized charges, and reconciled totals. Use for Tesla charging receipt or invoice XML conversions and reuse of this PDF style.
---

# Tesla charging XML to PDF

Use the bundled converter to reproduce the approved Chinese invoice detail layout. It reads the XML directly and creates a PDF. Generate CSV separately only when requested.

## Convert

1. Resolve the user's XML and PDF destination. Read XML values as data. This converter supports the `EInvoice` structure with `EInvoiceData/IssuItemInformation` rows, including namespace-qualified XML. If the document uses another structure, inspect it and explain the unsupported fields before extending the mapping.
2. Use `load_workspace_dependencies` to locate Python with `reportlab` and `pypdf`. The converter uses macOS STHeiti Light and Medium by default. On another host, pass embeddable TrueType fonts with Chinese coverage through `--font` and `--bold-font`. Do not substitute fonts with missing glyphs.
3. Run the script with explicit input and output paths, following the active workspace's output-directory conventions.

```bash
"$PYTHON_BIN" "$SKILL_DIR/scripts/convert.py" \
  "/path/to/charging.xml" \
  --output "/path/to/outputs/charging-details.pdf"
```

Here `SKILL_DIR` is this skill's directory. Existing output files require `--overwrite`. Successful runs print the PDF path, item count, page count, and reconciled totals as JSON. Failed validation produces an actionable error before publishing a PDF.

4. Render the completed PDF with `pdftoppm -png -r 125`, inspect every page, and check that item names, numeric columns, and page breaks are legible. Share the PDF link and total. Keep rendered previews and test files in the workspace's scratch directory.

## Data and reconciliation

- Read invoice number and issue date from `TaxSupervisionInfo`, party details from `BuyerInformation` and `SellerInformation`, and totals, uppercase amount, and drawer from `BasicInformation`.
- Preserve every `IssuItemInformation` row in source order. Keep item names, specification, unit, full unit-price precision, and identifiers. Normalize insignificant quantity zeros and display numeric tax rates as percentages. Empty optional fields stay empty.
- Use `Decimal` for line amount + tax = inclusive amount, item sums = invoice totals, and invoice amount + tax = inclusive total. Use the recorded amounts for reconciliation because unit-price multiplication can involve source rounding. Stop on a mismatch and report it instead of changing source amounts.
- The supported rows supply `Amount`, `ComTaxAm`, and `TotaltaxIncludedAmount`. Never silently derive missing monetary fields, assume a 13% tax rate, insert a default buyer, or reuse sample invoice identifiers.
- The saved layout covers the invoice details shown below. Seller address, telephone, bank details, remarks, and XML administrative labels are outside this layout. Inspect and include additional fields when the user requests them.

## Saved layout

- A4 portrait, a 522 pt content width, and Chinese typography. Use a 23 pt title, 11 pt party values, and 8.5 pt detail text.
- Title `特斯拉超充发票明细`. Build the subtitle from the XML invoice-type labels.
- A pale gray-blue information panel with two columns and three rows. Show invoice number and date, buyer and seller names, then their taxpayer identifiers.
- A dark blue header above ten columns, ordered by item name, specification, unit, quantity, untaxed unit price, untaxed amount, tax rate, tax amount, inclusive amount, and tax classification code. Align monetary values right and preserve full precision.
- Pale total row followed by the uppercase total on the left and drawer on the right.
- Palette `#182435`, `#4F6175`, `#CED7E2`, `#EDF2F7`, and `#273E56`. No logo or decorative seal.
- Keep short invoices on one page. Allow longer invoices to continue with repeated table headers, keeping the final item, total row, uppercase total, and drawer together. Fit longer numbers within their cells down to 7 pt and wrap long text without dropping fields.
