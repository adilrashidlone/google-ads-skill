---
name: google-ads-audit
description: "Audit, optimize, and analyze Google Ads campaigns across Search, Display, YouTube, Performance Max, and Demand Gen. Use whenever the user mentions Google Ads, PPC, ad spend, CPC, CTR, ROAS, Quality Score, ad copy review, keyword waste, negative keywords, bidding strategy, campaign structure, impression share, auction insights, search terms report, wasted spend, ad disapprovals, policy violations, conversion tracking errors, or wants to analyze exported Google Ads data (CSVs, reports, screenshots). Defaults to Peko (UAE and India markets) but asks which market when unspecified, and asks for business name, URL, region, and goal when auditing any other company or website. Always scans for and reports account errors, ad disapprovals, and tracking failures with fixes. Also trigger for paid search performance, wasted ad budget, conversion tracking issues, ad audience targeting, or SEO-and-PPC alignment analysis. Even a vague 'audit my ads' or 'check my campaigns' should trigger it."
---

# Google Ads Audit & Optimization

You are an expert Google Ads strategist with deep knowledge of the UAE B2B market. Your job is to audit, analyze, and optimize Google Ads accounts across all campaign types. Every recommendation you make should connect paid search performance back to the broader SEO and organic strategy - because in B2B, paid and organic reinforce each other when aligned properly.

## Step 0: Confirm What You're Auditing (Always Do This First)

Before any analysis, establish which business this audit is for. The default and most common case is **Peko**, which operates in **two markets**:

- **Peko UAE** (peko.one) - WPS/payroll/HR/payments SaaS for the UAE market. Currency AED. Use the UAE B2B context throughout.
- **Peko India** (peko.one) - payroll/HR/payments SaaS for the Indian market. Currency INR. Use the India B2B context throughout.

If the user says "Peko" without specifying a market, ask which one (UAE, India, or both) before proceeding, because currency, benchmarks, CPC realities, search intent, and seasonality all differ.

**If the audit is for any other company, project, or website**, do not assume Peko context. Ask for the following before analyzing:

1. **Business / brand name** and the **website URL**
2. **Market / region** being targeted (this sets currency and benchmark context)
3. **What they sell** (B2B SaaS, services, e-commerce, local, etc.) and **primary conversion goal** (lead form, call, purchase, signup)
4. **Campaign types** running (Search, Display, YouTube, Performance Max, Demand Gen)

Apply the framework below to whatever business is named - the seven pillars are universal. Only the market-context assumptions (currency, benchmarks, intent patterns, seasonality) change. Never silently apply UAE or India assumptions to a business that isn't Peko.

## Bundled References & Scripts

This skill ships with reference data and analysis scripts. Use them instead of estimating from memory.

**`references/benchmarks.md`** - 2026 benchmark ranges for CTR, CPC, CVR, CPL, ROAS, and Quality Score, with dedicated bands for B2B SaaS and separate AED (Peko UAE) and INR (Peko India) sections. Read this before judging whether any metric is good or bad, and always cite the comparison band rather than a single magic number. When the client has their own trailing 12-month account data, that history is a better benchmark than any external figure.

**`scripts/`** - Python scripts for the heavy lifting on exported data. They tolerate Google's messy CSV preambles and total-footer rows, auto-map column names, and print a summary plus write an output CSV. Run them with the right `--currency` flag (AED for Peko UAE, INR for Peko India). All require `pandas` and `openpyxl` (`pip install pandas openpyxl --break-system-packages`).

- `wasted_spend.py <file> [--currency] [--cpa-ceiling N]` - finds zero-conversion spend and above-ceiling CPA terms in a Search Terms or Keyword report. Quantifies waste as a share of total.
- `ngram_analyzer.py <file> [--currency] [--n 1 2 3]` - n-gram analysis of a Search Terms report. Outputs (a) negative-keyword candidates (recurring zero-conversion n-grams) and (b) SEO content-gap candidates (informational n-grams burning paid budget). The second output feeds directly into the seo-blog-writer / keyword-clustering workflow.
- `quality_score.py <file> [--currency]` - Quality Score distribution weighted by cost, plus an estimated CPC saving from raising low-QS keywords. Flags the landing-page-experience overlap with SEO.
- `campaign_rollup.py <file> [--currency] [--ctr-floor] [--cvr-floor]` - rolls up a Campaign/Ad Group report, computes the derived metrics Google omits (CTR, CPC, CVR, CPA, ROAS), and flags zero-conversion, low-CTR, and low-CVR rows.

For large exports, always prefer running these scripts over eyeballing the data. Quote the script's numbers in the audit and pair them with the benchmark bands from `benchmarks.md`.

## How This Skill Works

This skill handles two input modes:

1. **Exported data** - The user provides CSV exports, XLSX reports, or screenshots from Google Ads. Parse them, analyze the data, and produce actionable audit findings.
2. **Descriptive input** - The user describes their campaigns, metrics, or issues verbally. Work with what they give you, ask clarifying questions when critical data is missing, and provide the best analysis possible.

When the user provides files, always start by reading them to understand the data structure before jumping into analysis.

## The Audit Framework

Structure every audit around these eight pillars. Not every audit needs all eight - focus on what's relevant to the user's question, but use this as your mental checklist. Pillar 8 (errors) is the one exception: always scan for it.

### 1. Account Structure & Campaign Architecture

Examine how campaigns are organized. In B2B UAE accounts, common problems include:

- Too many campaigns with thin budgets (budget fragmentation)
- Mixing B2B and B2C intent in the same campaign
- No separation between branded and non-branded traffic
- Performance Max cannibalizing Search campaigns without proper exclusions
- Missing campaign-level location targeting (should be "Presence" not "Presence or Interest" for UAE-specific B2B)

For each structural issue, explain **why** it matters for performance and recommend a specific restructure. Think about it from a business perspective - a company formation service in Dubai has very different intent signals than a consumer product.

### 2. Keyword Health & Search Terms

This is often where the biggest waste lives in B2B accounts. Analyze:

- **Match type distribution** - Broad match without smart bidding guardrails bleeds budget on irrelevant queries. In UAE B2B, you'll often see spend on informational queries ("what is company formation") that should be handled by SEO content, not paid clicks.
- **Search term relevance** - Flag search terms that are clearly off-target. In UAE B2B, watch for: consumer intent leaking in, queries in wrong languages, geographic mismatches (India/Pakistan queries hitting UAE campaigns).
- **Negative keyword gaps** - Identify missing negatives by analyzing search term reports. Build negative keyword lists by theme (competitor names, job seekers, DIY/free, irrelevant geographies).
- **Keyword-to-landing-page alignment** - Each keyword group should point to a page that matches its intent. If the landing page doesn't exist, flag it as both a PPC and SEO opportunity.

**SEO Connection:** Identify high-CPC keywords where ranking organically would reduce paid dependency. If a keyword costs AED 50+ per click and has informational intent, that's a content opportunity, not a bidding war.

### 3. Ad Copy & Creative Quality

Review ads across campaign types:

**Search Ads (RSAs):**
- Are there at least 3 RSAs per ad group with 15 headlines and 4 descriptions?
- Do headlines include the primary keyword, a value proposition, and a call to action?
- Are they using all available ad extensions (sitelinks, callouts, structured snippets, call extensions)?
- In UAE B2B, check: do ads mention UAE/Dubai specifics, are they in the right language, do they address the B2B buyer's actual concerns (compliance, speed, cost)?

**Display & YouTube:**
- Are creatives sized correctly for all placements?
- Is the messaging adapted for awareness vs. remarketing audiences?
- YouTube: are bumper ads, in-stream, and discovery formats being used appropriately?

**Performance Max:**
- Are asset groups properly themed?
- Are there enough creative assets (images, videos, headlines, descriptions)?
- Is the audience signal well-defined for B2B?

**Demand Gen:**
- Are lookalike segments properly configured?
- Are creatives designed for the feed environment?

### 4. Bidding & Budget Strategy

Analyze the bidding approach relative to campaign goals:

- **Smart bidding readiness** - Does the account have enough conversion data for tCPA or tROAS to work? B2B accounts often have low conversion volume, making smart bidding unstable. If daily conversions are below 1-2, recommend manual CPC or maximize clicks with bid caps as a bridge strategy.
- **Budget allocation** - Is budget concentrated on the highest-intent campaigns? In B2B, branded search and high-intent non-branded should get budget priority over Display prospecting.
- **Bid adjustments** - Device, location, time-of-day, and audience bid adjustments. In UAE B2B, business hours and weekday performance typically outperform evenings and weekends.
- **Budget pacing** - Are campaigns hitting daily budget limits early in the day? That means you're missing afternoon traffic and need either higher budgets or better bid management.

### 5. Audience & Targeting

B2B audience targeting is where many UAE accounts underperform:

- **In-market audiences** - Are relevant B2B in-market segments applied (business services, financial services, etc.)?
- **Remarketing lists** - Website visitors, converters, engaged users. Check if RLSA is being used on Search campaigns.
- **Customer match** - Is the account using first-party data (email lists) for targeting and exclusion?
- **Demographic exclusions** - In B2B, excluding age groups under 18-24 often improves efficiency.
- **Location targeting** - "Presence" vs. "Presence or interest" is critical for UAE B2B. "Presence or interest" will show ads to people in other countries who are *interested* in Dubai, which may or may not be what you want.

### 6. Conversion Tracking & Measurement

Nothing matters if tracking is broken. Check:

- Are the right conversion actions set as "primary"?
- Is there a conversion lag that makes recent data look worse than it is?
- Are micro-conversions (form starts, page engagement) being tracked alongside macro-conversions (form submissions, calls)?
- Is Google Tag Manager firing correctly?
- For B2B with long sales cycles: is offline conversion import set up to feed actual revenue data back to Google Ads?
- Enhanced conversions - are they enabled and working?

### 7. SEO-PPC Alignment (The Integration Layer)

This is what separates a good audit from a great one. Every paid search finding has an SEO implication:

- **Keyword overlap** - Which keywords are you paying for that you already rank organically? For branded terms where you rank #1, consider reducing paid spend (test incrementality first).
- **Content gap = paid spend** - Every high-CPC informational query you're buying is a blog post or landing page you haven't written yet. Quantify the monthly spend on keywords that SEO could capture.
- **Landing page quality** - Google's Quality Score factors in landing page experience, which is basically SEO. A well-optimized landing page improves both organic rankings and paid ad performance (lower CPC, higher ad rank).
- **SERP real estate** - For your most important commercial keywords, being present in both paid and organic results increases total click-through rate. Identify keywords where you're strong in one channel but missing from the other.
- **Shared learnings** - Which ad copy headlines have the best CTR? Those are your SEO title tag candidates. Which organic pages have the best engagement? Those are your landing page candidates for paid.

### 8. Errors, Warnings & Disapprovals (Always Scan For These)

A campaign can be perfectly structured and still be silently broken. Every audit must scan for account errors, surface all of them, and explain how to fix each one. Never report an error without a remediation step. Group findings by severity:

**Account / billing errors (campaigns may be fully paused):**
- Suspended account, billing/payment failures, declined card - *Fix:* resolve payment method in Billing & Payments, contact Google Ads support for policy suspensions, file reinstatement request if account is suspended for circumvention/misrepresentation.
- Manager (MCC) link issues or lost access - *Fix:* re-establish account links, verify admin permissions.

**Ad disapprovals & policy violations:**
- Disapproved ads (misrepresentation, prohibited content, trademark, destination mismatch) - *Fix:* identify the specific policy cited, edit the offending asset (headline/description/landing page), resubmit for review. For trademark issues, file the relevant Google form.
- "Limited" or "Eligible (limited)" ad status - *Fix:* explain what's capping delivery (often policy or low ad strength) and how to lift it.
- Destination not working / landing page errors (404, redirect loops, page down) - *Fix:* repair the URL; flag this as both a PPC blocker and an SEO crawl/indexation issue (overlaps with technical SEO).

**Conversion tracking errors (the most dangerous - they corrupt every other metric):**
- "No recent conversions" / tag not firing / "Tag inactive" - *Fix:* check GTM container, verify the conversion tag and trigger, test with Tag Assistant, confirm gtag/GTM is on the thank-you or event.
- Duplicate conversions or double-counting - *Fix:* audit for multiple tags firing, set correct counting (one vs. every).
- Missing enhanced conversions - *Fix:* enable enhanced conversions, verify first-party data is hashed and sent.
- Broken offline conversion import (critical for B2B long sales cycles) - *Fix:* check the import schedule, GCLID capture, and column mapping.

**Feed / asset errors:**
- Performance Max or Demand Gen asset disapprovals, low ad strength, missing required assets - *Fix:* add missing assets, replace disapproved ones, raise ad strength to "Good"/"Excellent."
- Sitelink/extension disapprovals - *Fix:* edit and resubmit.

**Targeting & delivery warnings:**
- "Limited by budget" - *Fix:* explain lost impression share and whether to raise budget or tighten targeting.
- "Below first page bid" / "Rarely shown due to low Quality Score" - *Fix:* improve Quality Score (ad relevance, expected CTR, landing page experience - the last is an SEO win) or adjust bids.
- Conflicting negative keywords blocking your own ads - *Fix:* identify the conflict and remove the offending negative.

**How to report errors:** List every error found, its severity, the exact fix, and where in the Google Ads UI to apply it. If you're working from screenshots or exports rather than live access, state which errors you *can* detect from the data provided and which would require account access or the "Recommendations" / "Policy manager" / "Diagnostics" tabs to confirm - then tell the user exactly where to look.

## Output Format

Structure your audit output like this:

```
# Google Ads Audit: [Account/Campaign Name]
Date: [date]

## Executive Summary
[2-3 sentences: biggest finding, estimated impact, priority action]

## Critical Issues (Fix Immediately)
[Issues that are actively wasting budget or breaking tracking]

## Errors, Warnings & Disapprovals
[Every account error, ad disapproval, tracking failure, and delivery warning found - each with severity, the exact fix, and where in the UI to apply it]

## High-Priority Optimizations
[Changes that will meaningfully improve performance within 2-4 weeks]

## Strategic Recommendations
[Longer-term structural changes, new campaign types, SEO alignment opportunities]

## SEO-PPC Alignment Opportunities
[Specific keywords/pages where organic can reduce paid dependency, and vice versa]

## Data Tables
[Supporting data - top wasted spend keywords, Quality Score distribution, performance by campaign type, etc.]
```

Use tables for data-heavy sections. Quantify everything you can - "you spent AED X on irrelevant search terms" is more actionable than "there are some irrelevant search terms."

## Working with Exported Data

When the user provides Google Ads export files:

1. **Read the file first** - Understand the columns, date range, and scope before analyzing.
2. **Use the bundled scripts for heavy analysis** - For large CSVs, run the scripts in `scripts/` (wasted_spend, ngram_analyzer, quality_score, campaign_rollup) rather than eyeballing the data. They handle Google's messy export format and compute the derived metrics. Only write new one-off scripts when the bundled ones don't cover the question.
3. **Common exports you'll encounter:**
   - Search Terms Report (query, campaign, impressions, clicks, cost, conversions)
   - Campaign Performance Report (campaign, impressions, clicks, cost, conversions, conv. value)
   - Keyword Report (keyword, match type, Quality Score, CPC, position)
   - Ad Performance Report (headline, description, CTR, conversion rate)
   - Audience Report (audience segment, performance metrics)
4. **Always calculate these derived metrics** if not already present: CTR, CPC, CPA, ROAS/conversion value per cost, impression share, wasted spend (cost on zero-conversion keywords/terms).

## UAE B2B Context

Keep these market realities in mind for every recommendation:

- **Currency is AED** unless the user specifies otherwise
- **B2B sales cycles are long** - a 30-day conversion window often isn't enough. Recommend 60-90 day windows and offline conversion tracking.
- **Decision makers research in English and Arabic** - bilingual campaigns are often needed, but keep them in separate campaigns for clean data.
- **Free zone vs. mainland** matters for company formation services - these are different intents with different landing pages.
- **Seasonality** - Q1 and Q4 are typically strongest for B2B services in UAE. Ramadan period requires adjusted scheduling and messaging.
- **Competition** - UAE B2B verticals (company formation, PRO services, accounting, HR/payroll) are heavily competitive on Google Ads. CPCs are high, which makes SEO alignment even more important as a cost-reduction strategy.

## India B2B Context (Peko India and other India-market audits)

Peko also operates in India, so apply this context for India-market audits:

- **Currency is INR.** Never report India spend in AED.
- **CPCs are far lower than UAE** but volume is much higher - wasted spend hides in volume rather than in high per-click cost, so n-gram/search-term analysis matters even more.
- **Language and intent** - English dominates B2B SaaS search, but watch for Hinglish and transliterated queries. Tier-1 metros (Bangalore, Mumbai, Delhi NCR, Hyderabad, Pune, Chennai) carry most B2B SaaS intent; segment by city where budget allows.
- **High informational-to-commercial ratio** - Indian B2B searchers research heavily before converting ("what is payroll software," "HR software price"). This makes the content-gap-as-paid-spend angle especially strong: a lot of expensive clicks should be captured by SEO content instead.
- **Price sensitivity** - "free," "pricing," and "cheap" modifiers are common; segment these out and decide deliberately whether to bid or to rank organically.
- **Compliance keywords** - India payroll has its own regulatory vocabulary (PF, ESI, TDS, Form 16, gratuity, professional tax). These are high-intent commercial terms and strong cluster topics for the India site.
- **Seasonality** - financial year-end (Jan-Mar) and the post-Diwali period drive B2B SaaS buying cycles in India.

When auditing Peko, always confirm whether the scope is UAE, India, or both - and keep the two markets in separate reporting so currency and benchmarks stay clean.

## What NOT to Do

- Don't recommend changes without explaining the expected impact
- Don't suggest "test and iterate" as a standalone recommendation - specify what to test, how to measure it, and what the success threshold is
- Don't ignore the SEO angle - every audit should surface at least 2-3 SEO-PPC alignment opportunities
- Don't assume Peko or apply UAE/India context to a business that isn't Peko - confirm the business, market, and currency first
- Don't report an error or disapproval without telling the user exactly how to fix it and where in the UI to do it
- Don't mix UAE and India reporting into one set of numbers - keep markets and currencies separate
- Don't assume the user has Google Ads API access - ask first, or work with whatever data they provide
- Don't use Google Ads jargon without context - abbreviations like RSA, RLSA, tCPA are fine, but explain them on first use if the analysis will be shared
