#!/usr/bin/env python3
"""
quality_score.py - Quality Score distribution + CPC-savings opportunity.

From a Keyword report (with Quality Score and CPC/cost columns), this:
  - Buckets keywords by QS (1-3 poor, 4-6 average, 7-10 good)
  - Weights by cost so you see where money sits, not just keyword counts
  - Estimates the CPC discount available from raising low-QS keywords
    (rule of thumb: QS 5->8 ~30% cheaper; QS 10 ~80% cheaper than QS 1)

Usage:
    python quality_score.py <keyword_report.csv|xlsx> [--currency AED|INR|USD]

Output: printed summary + quality_score_priorities.csv (worst-QS, highest-cost first)
"""
import sys
import argparse

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas required: pip install pandas openpyxl --break-system-packages")


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
        errors="coerce")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--currency", default="")
    args = ap.parse_args()
    cur = f" {args.currency}" if args.currency else ""

    df = load_table(args.file)
    kw_col = find_col(df, ["keyword"])
    qs_col = find_col(df, ["quality score", "qual. score", "quality"])
    cost_col = find_col(df, ["cost", "spend"])
    if not qs_col:
        sys.exit(f"No Quality Score column found. Columns: {list(df.columns)}\n"
                 "Tip: enable the Quality Score column in the Google Ads keyword view before export.")

    df["_qs"] = to_num(df[qs_col])
    df["_cost"] = to_num(df[cost_col]).fillna(0) if cost_col else 0
    df = df.dropna(subset=["_qs"])

    def bucket(qs):
        if qs <= 3: return "1-3 Poor"
        if qs <= 6: return "4-6 Average"
        return "7-10 Good"

    df["_bucket"] = df["_qs"].apply(bucket)
    total_cost = df["_cost"].sum()

    print("=" * 60)
    print("QUALITY SCORE DISTRIBUTION")
    print("=" * 60)
    print(f"Keywords analyzed: {len(df)}   |   Avg QS: {df['_qs'].mean():.1f}")
    print()
    print(f"{'Bucket':<14}{'Keywords':>10}{'% kw':>7}{'Cost':>16}{'% cost':>8}")
    for b in ["1-3 Poor", "4-6 Average", "7-10 Good"]:
        sub = df[df["_bucket"] == b]
        kcount = len(sub)
        kcost = sub["_cost"].sum()
        print(f"{b:<14}{kcount:>10}{(kcount/len(df)*100):>6.0f}%"
              f"{kcost:>15,.2f}{cur}{(kcost/total_cost*100 if total_cost else 0):>7.0f}%")

    # Savings estimate: assume raising poor/avg keywords to QS 8 yields a CPC discount.
    # Conservative: 1-3 -> ~40% cheaper, 4-6 -> ~20% cheaper.
    poor_cost = df[df["_bucket"] == "1-3 Poor"]["_cost"].sum()
    avg_cost = df[df["_bucket"] == "4-6 Average"]["_cost"].sum()
    est_savings = poor_cost * 0.40 + avg_cost * 0.20
    print()
    print(f"Estimated CPC savings if low-QS keywords reach QS 8: "
          f"~{est_savings:,.2f}{cur} per period")
    print("(Heuristic: 1-3 buckets ~40% cheaper, 4-6 ~20% cheaper at QS 8.)")

    # Priority list: worst QS carrying the most cost
    prio = df[df["_qs"] <= 6].sort_values(["_cost"], ascending=False)
    out_cols = [c for c in [kw_col, qs_col, cost_col] if c]
    prio[out_cols].to_csv("quality_score_priorities.csv", index=False)
    print("\nTop QS fix priorities (low QS, high cost):")
    for _, r in prio.head(12).iterrows():
        kw = str(r[kw_col])[:45] if kw_col else "(kw)"
        print(f"  QS {r['_qs']:>2.0f} | {r['_cost']:>10,.2f}{cur} | {kw}")
    print("\nWritten: quality_score_priorities.csv")
    print("\nSEO tie-in: QS is driven partly by landing page experience. The same")
    print("page fixes that lift QS (speed, message match, relevance) lift organic rank.")


if __name__ == "__main__":
    main()
