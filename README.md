## Bundled scripts

Run these on exported data instead of estimating from memory. They tolerate Google's messy CSV preambles and total-footer rows, auto-map column names, print a summary, and write an output CSV. Use the right `--currency` flag (`AED` for UAE, `INR` for India).

| Script | What it does |
|--------|--------------|
| `scripts/wasted_spend.py <file> [--currency] [--cpa-ceiling N]` | Finds zero-conversion spend and above-ceiling CPA terms; quantifies waste as a share of total. |
| `scripts/ngram_analyzer.py <file> [--currency] [--n 1 2 3]` | N-gram analysis: (a) negative-keyword candidates, (b) **SEO content-gap candidates** (informational n-grams burning paid budget). |
| `scripts/quality_score.py <file> [--currency]` | Cost-weighted Quality Score distribution + estimated CPC saving from raising low-QS keywords; flags landing-page/SEO overlap. |
| `scripts/campaign_rollup.py <file> [--currency] [--ctr-floor] [--cvr-floor]` | Rolls up a Campaign/Ad Group report, computes CTR/CPC/CVR/CPA/ROAS, flags zero-conversion, low-CTR, low-CVR rows. |

```bash
python scripts/ngram_analyzer.py search_terms.csv --currency AED --n 1 2 3
```

---

## References

- **`references/benchmarks.md`** — 2026 benchmark ranges for CTR, CPC, CVR, CPL, ROAS, and Quality Score, with dedicated B2B SaaS bands and separate AED / INR sections. Read before judging any metric; cite the comparison band rather than a single number. When the client has trailing 12-month account data, that history beats any external benchmark.

---

## The audit framework (8 pillars)

1. **Account structure & campaign architecture** — budget fragmentation, B2B/B2C mixing, branded/non-branded separation, PMax cannibalization, location targeting
2. **Keyword health & search terms** — match-type distribution, search-term relevance, negative-keyword gaps, keyword-to-landing-page alignment
3. **Ad copy & creative quality** — RSAs, extensions, Display/YouTube/PMax/Demand Gen assets
4. **Bidding & budget strategy** — smart-bidding readiness, budget allocation, bid adjustments, pacing
5. **Audience & targeting** — in-market, remarketing/RLSA, customer match, demographic exclusions, Presence vs. Presence-or-interest
6. **Conversion tracking & measurement** — primary actions, conversion lag, micro vs. macro, offline import for long B2B cycles, enhanced conversions
7. **SEO-PPC alignment** — keyword overlap, content-gap-as-paid-spend, landing-page quality, SERP real estate, shared learnings
8. **Errors, warnings & disapprovals** — *always scanned* — billing, disapprovals, tracking failures, delivery warnings, each with a fix and UI location

---

## Output format

Audits are delivered as a structured report: Executive Summary → Critical Issues → Errors/Warnings/Disapprovals → High-Priority Optimizations → Strategic Recommendations → **SEO-PPC Alignment Opportunities** → Data Tables. Everything is quantified ("you spent AED X on irrelevant search terms"), data-heavy sections use tables, and every error ships with a remediation step.

---

## Topics

`google-ads` `ppc` `ppc-audit` `google-ads-audit` `seo` `seo-ppc-alignment` `wasted-spend` `negative-keywords` `quality-score` `claude-skill` `b2b-saas` `paid-search` `search-terms-report` `uae` `india`

---
## License

Copyright (c) 2026 Adil Rashid Lone. All rights reserved.

This is proprietary software developed for internal use. No part of this
repository may be reproduced, distributed, or used without express permission.
