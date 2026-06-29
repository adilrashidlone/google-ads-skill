#!/usr/bin/env python3
"""
wasted_spend.py - Find budget waste in a Google Ads Search Terms or Keyword report.

Flags:
  - Search terms / keywords with cost but ZERO conversions (pure waste)
  - High-cost / low-conversion-rate terms (inefficient, above a CPA ceiling)
  - Spend concentration (how much waste sits in the top offenders)

Usage:
    python wasted_spend.py <file.csv|file.xlsx> [--currency AED|INR|USD] [--cpa-ceiling N]

The script auto-detects common Google Ads column names (it tolerates the
header junk Google exports put at the top of CSVs). It does NOT assume a fixed
schema - it maps columns by fuzzy name match and tells you what it mapped.

Output: a printed summary plus a `wasted_spend_output.csv` with the flagged rows.
"""
import sys
import argparse
import re

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas required: pip install pandas openpyxl --break-system-packages")


# Fuzzy column name candidates (lowercased substring match)
COLMAP = {
    "term":   ["search term", "keyword", "search keyword"],
    "campaign": ["campaign"],
    "cost":   ["cost", "spend"],
    "conversions": ["conversions", "conv.", "conv "],
    "clicks": ["clicks"],
    "impressions": ["impr", "impressions"],
    "conv_value": ["conv. value", "conversion value", "all conv. value"],
}


def load_table(path):
    """Load CSV/XLSX, skipping Google's preamble rows until a real header is found."""
    if path.lower().endswith((".xlsx", ".xls")):
        raw = pd.read_excel(path, header=None)
    else:
        import csv as _csv
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
            rows = list(_csv.reader(fh))
        if not rows:
            sys.exit("Empty file.")
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        raw = pd.DataFrame(rows, dtype=str)
    # Find the header row: first row containing 'cost' or 'clicks' or 'campaign'
    # Score each candidate row by how many distinct column tokens it contains.
    # A real Google header row has several (cost, clicks, campaign, ...);
    # title/preamble rows have at most one.
    tokens = ["cost", "spend", "clicks", "impr", "campaign", "ad group",
              "search term", "keyword", "conversions", "conv.", "quality score",
              "match type"]
    header_idx, best_score = 0, 0
    for i in range(min(15, len(raw))):
        row = " ".join(str(x).lower() for x in raw.iloc[i].tolist())
        score = sum(1 for t in tokens if t in row)
        if score > best_score:
            best_score, header_idx = score, i
        if score >= 2 and i > 0:
            break
    df = raw.iloc[header_idx + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[header_idx].tolist()]
    df = df.dropna(how="all").reset_index(drop=True)
    # Drop Google's "Total" footer rows
    df = df[~df.iloc[:, 0].astype(str).str.lower().str.startswith(("total", "—", "--"))]
    return df


def map_columns(df):
    found = {}
    lower_cols = {c.lower(): c for c in df.columns}
    for key, candidates in COLMAP.items():
        for cand in candidates:
            match = next((orig for low, orig in lower_cols.items() if cand in low), None)
            if match:
                found[key] = match
                break
    return found


def to_num(series):
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^\d.\-]", "", regex=True).replace("", "0"),
        errors="coerce",
    ).fillna(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--currency", default="")
    ap.add_argument("--cpa-ceiling", type=float, default=None,
                    help="Flag terms with CPA above this as inefficient")
    args = ap.parse_args()

    df = load_table(args.file)
    cols = map_columns(df)
    print(f"Mapped columns: {cols}\n")

    if "cost" not in cols:
        sys.exit("Could not find a Cost/Spend column. Check the export.")

    df["_cost"] = to_num(df[cols["cost"]])
    df["_conv"] = to_num(df[cols["conversions"]]) if "conversions" in cols else 0
    df["_clicks"] = to_num(df[cols["clicks"]]) if "clicks" in cols else 0
    label = cols.get("term", df.columns[0])

    total_cost = df["_cost"].sum()
    cur = f" {args.currency}" if args.currency else ""

    # 1. Pure waste: cost > 0, conversions == 0
    zero_conv = df[(df["_cost"] > 0) & (df["_conv"] == 0)].copy()
    zero_conv = zero_conv.sort_values("_cost", ascending=False)
    waste_cost = zero_conv["_cost"].sum()

    print("=" * 60)
    print("WASTED SPEND ANALYSIS")
    print("=" * 60)
    print(f"Total cost in report:      {total_cost:,.2f}{cur}")
    print(f"Zero-conversion spend:     {waste_cost:,.2f}{cur} "
          f"({(waste_cost/total_cost*100 if total_cost else 0):.1f}% of total)")
    print(f"Zero-conversion items:     {len(zero_conv)}")
    print()
    print("Top 15 zero-conversion money pits:")
    for _, r in zero_conv.head(15).iterrows():
        print(f"  {r['_cost']:>10,.2f}{cur}  |  {str(r[label])[:60]}")

    # 2. Inefficient: above CPA ceiling
    inefficient = pd.DataFrame()
    if args.cpa_ceiling:
        conv_df = df[df["_conv"] > 0].copy()
        conv_df["_cpa"] = conv_df["_cost"] / conv_df["_conv"]
        inefficient = conv_df[conv_df["_cpa"] > args.cpa_ceiling].sort_values("_cpa", ascending=False)
        print()
        print(f"Terms above CPA ceiling ({args.cpa_ceiling:,.2f}{cur}): {len(inefficient)}")
        for _, r in inefficient.head(10).iterrows():
            print(f"  CPA {r['_cpa']:>9,.2f}{cur}  |  {str(r[label])[:55]}")

    # Output file
    out = zero_conv.copy()
    out["flag"] = "zero_conversion"
    if not inefficient.empty:
        inefficient = inefficient.copy()
        inefficient["flag"] = "above_cpa_ceiling"
        out = pd.concat([out, inefficient], ignore_index=True)
    out.to_csv("wasted_spend_output.csv", index=False)
    print(f"\nFull list written to wasted_spend_output.csv")
    print("\nSEO tie-in: review the zero-conversion list for informational queries")
    print("(how/what/guide/meaning). Those are content opportunities, not bid problems.")


if __name__ == "__main__":
    main()
