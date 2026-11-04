#!/usr/bin/env python3
"""Convert Tesla EInvoice XML into the saved Chinese PDF layout."""

import argparse
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.platypus.doctemplate import LayoutError


DETAIL_FIELDS = (
    "ItemName", "SpecMod", "MeaUnits", "Quantity", "UnPrice", "Amount",
    "TaxRate", "ComTaxAm", "TotaltaxIncludedAmount", "TaxClassificationCode",
)
TOTAL_FIELDS = ("TotalAmWithoutTax", "TotalTaxAm", "TotalTax-includedAmount")
MONEY_FIELDS = ("Amount", "ComTaxAm", "TotaltaxIncludedAmount")
INK = colors.HexColor("#182435")
MUTED = colors.HexColor("#4F6175")
LINE = colors.HexColor("#CED7E2")
PALE = colors.HexColor("#EDF2F7")
NAVY = colors.HexColor("#273E56")


def get_text(node, path, required=False):
    value = node.findtext(path, default="").strip()
    if required and not value:
        raise ValueError(f"Missing required XML field: {path}")
    return value


def number(value, label):
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid number in {label}: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"Non-finite number in {label}: {value!r}")
    return result


def plain_number(value):
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def reconcile(actual, expected, label):
    if actual != expected:
        raise ValueError(f"Amount mismatch for {label}: calculated {actual}, XML {expected}")


def read_invoice(path):
    root = ET.parse(path).getroot()
    for element in root.iter():
        element.tag = element.tag.rsplit("}", 1)[-1]
    if root.tag != "EInvoice":
        raise ValueError(f"Unsupported XML root: {root.tag}. Expected EInvoice.")
    data = root.find("EInvoiceData")
    if data is None:
        raise ValueError("Missing required XML element: EInvoiceData")

    seller = get_text(data, "SellerInformation/SellerName", required=True)
    if "特斯拉" not in seller and "tesla" not in seller.casefold():
        raise ValueError("The seller name does not identify a Tesla invoice.")
    metadata = {
        "发票号码": get_text(root, "TaxSupervisionInfo/InvoiceNumber", True),
        "开票日期": get_text(root, "TaxSupervisionInfo/IssueTime", True),
        "购买方": get_text(data, "BuyerInformation/BuyerName", True),
        "购买方纳税人识别号": get_text(data, "BuyerInformation/BuyerIdNum"),
        "销售方": seller,
        "销售方纳税人识别号": get_text(data, "SellerInformation/SellerIdNum"),
        "开票人": get_text(data, "BasicInformation/Drawer"),
        "价税合计（大写）": get_text(data, "BasicInformation/TotalTax-includedAmountInChinese"),
    }
    types = [get_text(root, f"Header/InherentLabel/{tag}/LabelName")
             for tag in ("EInvoiceType", "GeneralOrSpecialVAT")]
    subtitle = f"{types[0]}（{types[1]}）" if all(types) else "".join(types)
    totals = [get_text(data, f"BasicInformation/{field}", True) for field in TOTAL_FIELDS]
    numeric_totals = [number(value, field) for value, field in zip(totals, TOTAL_FIELDS)]
    rows = []
    sums = [Decimal(0), Decimal(0), Decimal(0)]
    for index, item in enumerate(data.findall("IssuItemInformation"), start=1):
        values = {field: get_text(item, field, field in MONEY_FIELDS or field == "ItemName")
                  for field in DETAIL_FIELDS}
        amounts = [number(values[field], f"item {index}/{field}") for field in MONEY_FIELDS]
        reconcile(amounts[0] + amounts[1], amounts[2], f"item {index} inclusive amount")
        sums = [subtotal + amount for subtotal, amount in zip(sums, amounts)]
        if values["Quantity"]:
            values["Quantity"] = plain_number(number(values["Quantity"], f"item {index}/Quantity"))
        if values["UnPrice"]:
            number(values["UnPrice"], f"item {index}/UnPrice")
        if values["TaxRate"]:
            rate = number(values["TaxRate"], f"item {index}/TaxRate")
            values["TaxRate"] = plain_number(rate * 100) + "%"
        rows.append([values[field] for field in DETAIL_FIELDS])
    if not rows:
        raise ValueError("No IssuItemInformation rows found.")
    for total, expected, label in zip(sums, numeric_totals, TOTAL_FIELDS):
        reconcile(total, expected, label)
    reconcile(numeric_totals[0] + numeric_totals[1], numeric_totals[2], "invoice inclusive total")
    return metadata, subtitle, rows, totals


def register_fonts(regular_path, bold_path, values):
    for name, path in (("Heiti", regular_path), ("HeitiMedium", bold_path)):
        if not path.is_file():
            raise ValueError(f"Chinese font not found: {path}. Supply --font and --bold-font.")
        font = TTFont(name, str(path))
        missing = sorted({char for value in values for char in value
                          if not char.isspace() and ord(char) not in font.face.charWidths})
        if missing:
            raise ValueError(f"Font {path.name} is missing glyphs: {''.join(missing)}")
        pdfmetrics.registerFont(font)


def para(value, size=10, color=INK, align=TA_LEFT, strong=False):
    return Paragraph(escape(value), ParagraphStyle(
        "cell", fontName="HeitiMedium" if strong else "Heiti", fontSize=size,
        leading=size * 1.45, alignment=align, textColor=color, wordWrap="CJK",
    ))


def render_pdf(output, metadata, subtitle, rows, totals):
    meta_rows = []
    for labels in (("发票号码", "开票日期"), ("购买方", "销售方"),
                   ("购买方纳税人识别号", "销售方纳税人识别号")):
        meta_rows.append([[para(label, 9, MUTED), Spacer(1, 3), para(metadata[label], 11)]
                          for label in labels])
    meta_table = Table(meta_rows, colWidths=[261, 261], hAlign="LEFT")
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 13),
        ("RIGHTPADDING", (0, 0), (-1, -1), 13),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, -2), 0.45, colors.white),
    ]))

    headers = ["项目名称", "规格", "单位", "数量", "未税单价", "未税金额",
               "税率", "税额", "价税合计", "税收分类编码"]
    alignments = [TA_LEFT, TA_CENTER, TA_CENTER, TA_RIGHT, TA_RIGHT,
                  TA_RIGHT, TA_RIGHT, TA_RIGHT, TA_RIGHT, TA_LEFT]
    widths = [85, 29, 27, 28, 86, 48, 33, 39, 47, 100]
    table_rows = [[para(label, 8.5, colors.white, align, True)
                   for label, align in zip(headers, alignments)]]
    total_row = ["合计", "", "", "", "", totals[0], "", totals[1], totals[2], ""]
    for index, row in enumerate([*rows, total_row]):
        cells = []
        strong = index == len(rows)
        for column, (value, align, width) in enumerate(zip(row, alignments, widths)):
            size = 8.5
            if column >= 3 and value:
                font = "HeitiMedium" if strong else "Heiti"
                text_width = pdfmetrics.stringWidth(value, font, size)
                size = max(7, min(size, size * (width - 8) / text_width))
            cells.append(para(value, size, INK, align, strong))
        table_rows.append(cells)

    summary = Table([[
        para("价税合计（大写）  " + metadata["价税合计（大写）"]),
        para("开票人  " + metadata["开票人"], align=TA_RIGHT),
    ]], colWidths=[360, 162], hAlign="LEFT")
    summary.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    table_rows.append([summary] + [""] * 9)
    detail = Table(table_rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    detail.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, -2), (-1, -2), PALE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -3), 0.45, LINE),
        ("SPAN", (0, -1), (-1, -1)),
        ("NOSPLIT", (0, -3), (-1, -1)),
        ("LEFTPADDING", (0, -1), (-1, -1), 0),
        ("RIGHTPADDING", (0, -1), (-1, -1), 0),
        ("TOPPADDING", (0, -1), (-1, -1), 12),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 0),
    ]))
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=30, rightMargin=30,
                            topMargin=43, bottomMargin=40, title="特斯拉超充发票明细")
    doc.build([
        para("特斯拉超充发票明细", 23, strong=True), Spacer(1, 5),
        para(subtitle, 10, MUTED), Spacer(1, 22),
        meta_table, Spacer(1, 23),
        para("收费明细（金额单位为元）", 11, NAVY, strong=True), Spacer(1, 8),
        detail,
    ])


def verify_pdf(path, values):
    pdf = PdfReader(path)
    text = "".join(page.extract_text() or "" for page in pdf.pages)
    compact_text = "".join(text.split())
    for value in values:
        if "".join(value.split()) not in compact_text:
            raise ValueError(f"Text missing from generated PDF: {value!r}")
    return len(pdf.pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Tesla EInvoice XML")
    parser.add_argument("--output", type=Path, required=True, help="Destination PDF")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output PDF")
    parser.add_argument("--font", type=Path, default=Path("/System/Library/Fonts/STHeiti Light.ttc"))
    parser.add_argument("--bold-font", type=Path, default=Path("/System/Library/Fonts/STHeiti Medium.ttc"))
    args = parser.parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output == source or output.suffix.lower() != ".pdf":
        parser.error("Use a separate .pdf output path.")
    if output.exists() and not args.overwrite:
        parser.error("Output already exists. Choose another path or pass --overwrite.")

    temporary = None
    try:
        with localcontext() as context:
            context.prec = 50
            metadata, subtitle, rows, totals = read_invoice(source)
        values = [subtitle, *metadata.values(), *totals, *(cell for row in rows for cell in row)]
        labels = ("特斯拉超充发票明细电子发票收费明细金额单位为元项目名称规格单位数量"
                  "未税单价未税金额税率税额价税合计税收分类编码开票人发票号码开票日期"
                  "购买方销售方纳税人识别号大写（）")
        register_fonts(args.font.expanduser(), args.bold_font.expanduser(), [*values, labels])
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".tesla-", suffix=".pdf", dir=output.parent,
                                         delete=False) as temporary_file:
            temporary = Path(temporary_file.name)
        render_pdf(temporary, metadata, subtitle, rows, totals)
        pages = verify_pdf(temporary, values)
        if args.overwrite:
            os.replace(temporary, output)
        else:
            os.link(temporary, output)
        print(json.dumps({"output": str(output), "items": len(rows), "pages": pages,
                          "untaxed_amount": totals[0], "tax": totals[1], "total": totals[2]},
                         ensure_ascii=False))
    except (OSError, ValueError, ET.ParseError, TTFError, LayoutError) as exc:
        parser.exit(1, f"Conversion failed: {exc}\n")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
