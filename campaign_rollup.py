#!/usr/bin/env python3
"""
campaign_rollup.py - Roll up a Campaign or Ad Group performance report and
compute the derived metrics Google exports usually omit.

Computes per row and in totals: CTR, CPC, CVR, CPA, ROAS (if conv value present).
Flags rows that breach simple guardrails (zero-conversion spend, CTR or CVR
below a floor) so the worst campaigns surface immediately.

Usage:
    python campaign_rollup.py <campaign_report.csv|xlsx> [--currency AED|INR|USD]
           [--ctr-floor 0.02] [--cvr-floor 0.02]

Output: printed table + campaign_rollup_output.csv
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
        errors="coerce").fillna(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--currency", default="")
    ap.add_argument("--ctr-floor", type=float, default=0.02)
    ap.add_argument("--cvr-floor", type=float, default=0.02)
    args = ap.parse_args()
    cur = f" {args.currency}" if args.currency else ""

    df = load_table(args.file)
    name_col = find_col(df, ["campaign", "ad group"]) or df.columns[0]
    impr_col = find_col(df, ["impr"])
    clicks_col = find_col(df, ["clicks"])
    cost_col = find_col(df, ["cost", "spend"])
    conv_col = find_col(df, ["conversions", "conv."])
    val_col = find_col(df, ["conv. value", "conversion value", "all conv. value"])

    if not cost_col or not clicks_col:
        sys.exit(f"Need cost and clicks columns. Found: {list(df.columns)}")

    df["impressions"] = to_num(df[impr_col]) if impr_col else 0
    df["clicks"] = to_num(df[clicks_col])
    df["cost"] = to_num(df[cost_col])
    df["conversions"] = to_num(df[conv_col]) if conv_col else 0
    df["conv_value"] = to_num(df[val_col]) if val_col else 0

    df["CTR"] = (df["clicks"] / df["impressions"]).where(df["impressions"] > 0, 0)
    df["CPC"] = (df["cost"] / df["clicks"]).where(df["clicks"] > 0, 0)
    df["CVR"] = (df["conversions"] / df["clicks"]).where(df["clicks"] > 0, 0)
    df["CPA"] = (df["cost"] / df["conversions"]).where(df["conversions"] > 0, 0)
    df["ROAS"] = (df["conv_value"] / df["cost"]).where(df["cost"] > 0, 0)

    # Flags
    def flags(r):
        f = []
        if r["cost"] > 0 and r["conversions"] == 0:
            f.append("ZERO-CONV-SPEND")
        if r["impressions"] > 100 and r["CTR"] < args.ctr_floor:
            f.append("LOW-CTR")
        if r["clicks"] > 50 and r["CVR"] < args.cvr_floor:
            f.append("LOW-CVR")
        return ",".join(f)
    df["flags"] = df.apply(flags, axis=1)

    # Totals
    tot_cost = df["cost"].sum()
    tot_clicks = df["clicks"].sum()
    tot_impr = df["impressions"].sum()
    tot_conv = df["conversions"].sum()
    tot_val = df["conv_value"].sum()

    print("=" * 70)
    print("CAMPAIGN / AD GROUP ROLL-UP")
    print("=" * 70)
    print(f"Total spend:       {tot_cost:,.2f}{cur}")
    print(f"Total clicks:      {tot_clicks:,.0f}")
    print(f"Blended CTR:       {(tot_clicks/tot_impr*100 if tot_impr else 0):.2f}%")
    print(f"Blended CPC:       {(tot_cost/tot_clicks if tot_clicks else 0):,.2f}{cur}")
    print(f"Total conversions: {tot_conv:,.1f}")
    print(f"Blended CVR:       {(tot_conv/tot_clicks*100 if tot_clicks else 0):.2f}%")
    print(f"Blended CPA:       {(tot_cost/tot_conv if tot_conv else 0):,.2f}{cur}")
    if tot_val:
        print(f"Blended ROAS:      {(tot_val/tot_cost if tot_cost else 0):.2f}x")

    flagged = df[df["flags"] != ""].sort_values("cost", ascending=False)
    print(f"\nFlagged rows: {len(flagged)} (sorted by spend)")
    for _, r in flagged.head(15).iterrows():
        print(f"  {r['cost']:>10,.2f}{cur} | CTR {r['CTR']*100:>4.1f}% "
              f"CVR {r['CVR']*100:>4.1f}% | {r['flags']:<32} | {str(r[name_col])[:35]}")

    out = df[[name_col, "impressions", "clicks", "cost", "conversions",
              "conv_value", "CTR", "CPC", "CVR", "CPA", "ROAS", "flags"]]
    out.to_csv("campaign_rollup_output.csv", index=False)
    print("\nWritten: campaign_rollup_output.csv")


if __name__ == "__main__":
    main()
