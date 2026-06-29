#!/usr/bin/env python3
"""
ngram_analyzer.py - N-gram analysis of a Google Ads Search Terms report.

Two jobs in one:
  1. NEGATIVE KEYWORD MINING - surface recurring words/phrases that cost money
     and rarely convert, grouped so you can build themed negative lists.
  2. SEO CONTENT-GAP MINING - surface high-spend INFORMATIONAL n-grams
     (how/what/why/guide/meaning/vs/etc.) that should be captured by organic
     content instead of paid clicks.

Usage:
    python ngram_analyzer.py <search_terms.csv|xlsx> [--currency AED|INR|USD] [--n 1 2 3]

Output: printed tables + ngram_negatives.csv and ngram_seo_gaps.csv
"""
import sys
import argparse
import re
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas required: pip install pandas openpyxl --break-system-packages")

STOP = set("a an the of for to in on and or with your you my our we is are be at by from this that".split())
INFORMATIONAL = set("how what why when which who guide tutorial meaning definition vs versus "
                    "free example examples tips difference benefits explained list best top "
                    "vs. review reviews comparison".split())


def load_table(path):
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
    df = df[~df.iloc[:, 0].astype(str).str.lower().str.startswith(("total", "—", "--"))]
    return df


def find_col(df, candidates):
    for c in df.columns:
        for cand in candidates:
            if cand in c.lower():
                return c
    return None


def to_num(series):
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^\d.\-]", "", regex=True).replace("", "0"),
        errors="coerce").fillna(0)


def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOP and len(w) > 1]


def ngrams(tokens, n):
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--currency", default="")
    ap.add_argument("--n", nargs="+", type=int, default=[1, 2, 3])
    args = ap.parse_args()
    cur = f" {args.currency}" if args.currency else ""

    df = load_table(args.file)
    term_col = find_col(df, ["search term", "keyword"])
    cost_col = find_col(df, ["cost", "spend"])
    conv_col = find_col(df, ["conversions", "conv."])
    if not term_col or not cost_col:
        sys.exit(f"Need a search-term and cost column. Found columns: {list(df.columns)}")

    df["_cost"] = to_num(df[cost_col])
    df["_conv"] = to_num(df[conv_col]) if conv_col else 0

    agg = defaultdict(lambda: {"cost": 0.0, "conv": 0.0, "count": 0})
    info_agg = defaultdict(lambda: {"cost": 0.0, "conv": 0.0, "count": 0})

    for _, row in df.iterrows():
        toks = tokenize(row[term_col])
        is_info = any(t in INFORMATIONAL for t in toks)
        for n in args.n:
            for g in ngrams(toks, n):
                agg[g]["cost"] += row["_cost"]
                agg[g]["conv"] += row["_conv"]
                agg[g]["count"] += 1
                if is_info:
                    info_agg[g]["cost"] += row["_cost"]
                    info_agg[g]["conv"] += row["_conv"]
                    info_agg[g]["count"] += 1

    # NEGATIVE candidates: high cost, zero/low conversions, appears 2+ times
    neg = [(g, v["cost"], v["conv"], v["count"]) for g, v in agg.items()
           if v["count"] >= 2 and v["conv"] == 0 and v["cost"] > 0]
    neg.sort(key=lambda x: x[1], reverse=True)

    print("=" * 60)
    print("NEGATIVE KEYWORD CANDIDATES (recurring, zero-conversion n-grams)")
    print("=" * 60)
    print(f"{'cost':>12} {'#terms':>7}  n-gram")
    for g, cost, conv, cnt in neg[:25]:
        print(f"{cost:>12,.2f}{cur} {cnt:>7}  {g}")

    pd.DataFrame(neg, columns=["ngram", "cost", "conversions", "term_count"]
                 ).to_csv("ngram_negatives.csv", index=False)

    # SEO content-gap candidates: informational n-grams with real spend
    gaps = [(g, v["cost"], v["conv"], v["count"]) for g, v in info_agg.items()
            if v["cost"] > 0]
    gaps.sort(key=lambda x: x[1], reverse=True)

    print("\n" + "=" * 60)
    print("SEO CONTENT-GAP CANDIDATES (informational n-grams burning paid budget)")
    print("=" * 60)
    print("These should likely be captured by organic content, not paid clicks.")
    print(f"{'paid cost':>12} {'#terms':>7}  n-gram")
    total_gap = 0
    for g, cost, conv, cnt in gaps[:25]:
        total_gap += cost
        print(f"{cost:>12,.2f}{cur} {cnt:>7}  {g}")
    print(f"\nTop-25 informational paid spend (content-capturable): "
          f"{total_gap:,.2f}{cur}")
    print("Feed these into the seo-blog-writer / keyword-clustering workflow.")

    pd.DataFrame(gaps, columns=["ngram", "paid_cost", "conversions", "term_count"]
                 ).to_csv("ngram_seo_gaps.csv", index=False)
    print("\nWritten: ngram_negatives.csv, ngram_seo_gaps.csv")


if __name__ == "__main__":
    main()
