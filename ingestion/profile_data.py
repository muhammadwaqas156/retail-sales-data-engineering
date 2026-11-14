"""Profile the UCI Online Retail II workbook and the DummyJSON extracts.

Writes docs/source_profile.md. Usage:
  python -m ingestion.profile_data [path/to/online_retail_II.xlsx]
"""
import json
import sys
from pathlib import Path

import pandas as pd

from src.config import RAW_DIR, ROOT


def profile_uci(xlsx: Path) -> str:
    sheets = pd.read_excel(xlsx, sheet_name=None, dtype={"Customer ID": "string"})
    df = pd.concat(sheets.values(), ignore_index=True)
    inv = df["Invoice"].astype("string")
    cancelled = inv.str.startswith("C", na=False)
    lines = [f"## UCI Online Retail II ({xlsx.name})", "",
             f"- Sheets: {', '.join(sheets)} | Rows: {len(df):,} | Columns: {', '.join(df.columns)}",
             f"- Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}",
             f"- Distinct invoices: {inv.nunique():,} | customers: {df['Customer ID'].nunique():,} | "
             f"stock codes: {df['StockCode'].nunique():,}",
             f"- Fully duplicated rows: {df.duplicated().sum():,}",
             f"- Cancelled invoices (prefix 'C') rows: {int(cancelled.sum()):,}",
             f"- Rows with Quantity <= 0: {int((df['Quantity'] <= 0).sum()):,}",
             f"- Rows with Price <= 0: {int((df['Price'] <= 0).sum()):,}", "",
             "### Nulls per column", "", "| Column | Nulls | % |", "|---|---|---|"]
    for c, n in df.isna().sum().items():
        lines.append(f"| {c} | {n:,} | {n / len(df):.2%} |")
    return "\n".join(lines)


def profile_api() -> str:
    lines = ["## DummyJSON extracts (synthetic demo data)", ""]
    for name in ("products", "carts", "users"):
        files = sorted((RAW_DIR / name).glob("*.json"))
        if not files:
            lines.append(f"- {name}: no extract found (run ingestion.fetch_dummyjson)")
            continue
        data = json.loads(files[-1].read_text())
        items = data[name]
        keys = sorted({k for i in items for k in i})
        lines.append(f"- {name}: {len(items)} records; fields: {', '.join(keys)}")
    return "\n".join(lines)


def main() -> None:
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW_DIR / "online_retail_II.xlsx"
    parts = ["# Source data profile", ""]
    parts.append(profile_uci(xlsx) if xlsx.exists() else f"## UCI: file not found at {xlsx}")
    parts += ["", profile_api()]
    out = ROOT / "docs" / "source_profile.md"
    out.write_text("\n".join(parts) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
