"""Answer the four open checks in docs/business_rules.md.
Usage: python -m ingestion.check_rules  (writes docs/rule_checks.md)
"""
import sys
from pathlib import Path

import pandas as pd

from src.config import RAW_DIR, ROOT


def main() -> None:
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW_DIR / "online_retail_II.xlsx"
    df = pd.concat(pd.read_excel(xlsx, sheet_name=None, dtype={"Customer ID": "string"}).values(),
                   ignore_index=True)
    inv = df["Invoice"].astype("string")
    c = inv.str.startswith("C", na=False)
    out = ["# Rule check results", ""]

    out += ["## 1. Are all C rows Quantity < 0?",
            f"- C rows: {int(c.sum()):,} | with Quantity < 0: {int((c & (df.Quantity < 0)).sum()):,} "
            f"| with Quantity >= 0: {int((c & (df.Quantity >= 0)).sum()):,}", ""]

    adj = ~c & (df.Quantity <= 0)
    out += ["## 2. Non-C rows with Quantity <= 0",
            f"- Count: {int(adj.sum()):,}",
            f"- Price == 0: {int((adj & (df.Price == 0)).sum()):,}",
            f"- Customer ID null: {int((adj & df['Customer ID'].isna()).sum()):,}",
            f"- Description null: {int((adj & df.Description.isna()).sum()):,}",
            "- Top descriptions:", ""]
    out += [f"  - {k}: {v}" for k, v in df.loc[adj, "Description"].value_counts().head(10).items()]

    sc = df["StockCode"].astype("string")
    odd = df[~sc.str.match(r"^\d{5}[A-Za-z]*$", na=False)]
    out += ["", "## 3. StockCodes not matching ^\\d{5}[A-Za-z]*$",
            f"- Distinct codes: {odd.StockCode.nunique():,} | rows: {len(odd):,}",
            "- Most common:", ""]
    out += [f"  - {k}: {v:,}" for k, v in odd.StockCode.astype("string").value_counts().head(25).items()]

    dup = df[df.duplicated(keep=False)].sort_values(list(df.columns))
    same_inv = df[df.duplicated()].Invoice.nunique()
    out += ["", "## 4. Duplicates",
            f"- Duplicate rows (extra copies): {int(df.duplicated().sum()):,} across {same_inv:,} invoices",
            "- Sample (first 10 rows):", "", dup.head(10).to_markdown(index=False)]

    neg_price = df[df.Price < 0]
    out += ["", "## Extra: negative prices",
            f"- Rows: {len(neg_price):,}", neg_price.Description.value_counts().head(5).to_string()]
    p = ROOT / "docs" / "rule_checks.md"
    p.write_text("\n".join(out) + "\n")
    print(f"Wrote {p}")


if __name__ == "__main__":
    main()