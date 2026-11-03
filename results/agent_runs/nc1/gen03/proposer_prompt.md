You are a quantitative valuation researcher. Your job is to discover comparable-company
("comps") recipes that value US non-financial firms more accurately than standard methods.

TASK
Propose exactly 6 NEW recipes (generation 3). Accuracy is the median of |ln(V_est / V)|
across firm-years, where V is the firm's actual enterprise value on June 30 after its fiscal year.
Lower is better. Recipes are scored only on exploration years FY2016-2019; the
best ones will later be tested ONCE on later years you will never see, so prefer rules with a
clear economic reason over fragile tweaks. Cover both multiples across your proposals.

RECIPE LANGUAGE
A recipe is one firm-agnostic peer-selection rule. For every target firm in every year the
engine (1) takes all other firms in the same fiscal year with a positive multiple (the target
itself is always excluded), (2) applies the hard screens in "filters", (3) if fewer than
"min_peers" survive, tries each "fallback" screen set in order, (4) ranks survivors by a
weighted distance on within-year z-scores of the "rank" features and keeps the "k" nearest,
(5) aggregates the peers' multiples with "agg" and multiplies by the target's own driver.

Fields
  multiple:   one of ['EV/EBITDA', 'EV/Sales']  (EV/EBITDA uses firms with positive EBITDA)
  filters:    list of screens, each either {"same": GROUP} or {"band": {"var": FEATURE, "width": number}}
              GROUP is one of ['industry_l2', 'industry_l3', 'industry_l4']  (2-, 3- and 4-digit SIC codes)
              a band keeps candidates whose feature is within ±width of the target's (raw units)
  rank:       {FEATURE: positive weight, ...}  (empty = no ranking; then k must be "all")
  k:          "all" or an integer 3-30
  agg:        one of ['harmonic_mean', 'mean', 'median', 'trimmed_mean']
  min_peers:  positive integer (default 3)
  fallback:   list of filter lists tried in order when too few peers survive

FEATURES (accounting only; ratio features are winsorized 1%/99% each year)
  - log_sales: log of sales (size)
  - log_assets: log of total assets (size)
  - sales_growth_1y: 1-year sales growth
  - sales_growth_3y: 3-year annualized sales growth (missing for FY2016-2017: not enough history)
  - gross_margin: gross profit / sales
  - ebitda_margin: EBITDA / sales
  - ebit_margin: EBIT / sales
  - net_margin: net income / sales
  - roic: EBIT x (1 - 25%) / (equity + debt - cash)
  - roe: net income / book equity
  - asset_turnover: sales / total assets
  - net_debt_to_ebitda: (debt - cash) / EBITDA
  - debt_to_assets: total debt / total assets
  - rnd_intensity: R&D / sales
  - capex_intensity: capital expenditure / sales

HARD RULES
  - No market-based inputs (price, market cap, EV) for the target: they are the answer.
  - Missing feature values: a target missing ALL rank features gets no estimate; candidates
    missing a used rank feature are dropped. Low coverage is penalized by the selection rule.

BASELINES (exploration years)
  EV/EBITDA: Industry median (L3, fallback L2) median 0.333, mean 0.513; Warranted multiple (Bhojraj-Lee regression) median 0.357, mean 0.492; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.380, mean 0.523
  EV/Sales: Industry median (L3, fallback L2) median 0.603, mean 0.945; Warranted multiple (Bhojraj-Lee regression) median 0.674, mean 0.837; Warranted-multiple peers (Bhojraj-Lee, k=8) median 0.691, mean 0.861

ARCHIVE: your earlier graded attempts, exploration scores only (12 graded)
  [g02-06] EV/EBITDA median 0.320 | mean 0.489 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.025
      EV/EBITDA | screen same industry_l4 | rank sales_growth_1y 1, roic 1, ebit_margin 0.5, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l3] -> [same industry_l2] -> []
      mechanism: Four-digit SIC peers share product markets and so closer growth and risk outlooks; falling back to L3 then L2 keeps coverage. Including EBIT margin alongside ROIC proxies the share of EBITDA consumed by depreciation (asset intensity), so peers with similar EBIT-to-EBITDA conversion and growth should carry similar EBITDA multiples.
  [g01-01] EV/EBITDA median 0.322 | mean 0.484 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.030
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: Within a 3-digit industry, EV/EBITDA differences are driven mainly by expected growth, return on capital (reinvestment efficiency) and risk. Picking the industry peers closest on growth, ROIC, leverage and size should remove the within-industry dispersion that an unconditional industry median ignores.
  [g02-04] EV/EBITDA median 0.324 | mean 0.486 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.028
      EV/EBITDA | screen same industry_l3 | rank sales_growth_1y 1, roic 1, capex_intensity 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/EBITDA capitalizes cash earnings before reinvestment, so firms that must spend more of EBITDA on capex deserve lower multiples at the same growth. Adding capital intensity to the growth, ROIC, leverage and size match of g01-01 should align peers on free-cash-flow conversion, the piece EBITDA hides.
  [g02-05] EV/EBITDA median 0.331 | mean 0.499 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.014
      EV/EBITDA | screen same industry_l2, band sales_growth_1y±0.1 | rank sales_growth_1y 1, roic 1, net_debt_to_ebitda 0.5, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> [band sales_growth_1y±0.1] -> []
      mechanism: Expected growth is the main within-industry driver of EV/EBITDA, so a hard growth band inside the 2-digit industry guarantees peers on a similar growth path while the larger pool allows tighter matching on return on capital, leverage and size. This mirrors the margin-band success for EV/Sales, applied to the dominant EV/EBITDA driver.
  [g01-02] EV/EBITDA median 0.336 | mean 0.516 | coverage 100.0% | beats industry 2/4 yrs | gain vs industry -0.002
      EV/EBITDA | screen same industry_l2 | rank log_sales 1, ebitda_margin 1, sales_growth_1y 1, roic 0.5 | k=12, harmonic_mean, min_peers=5 | fallback []
      mechanism: Broader 2-digit industries give a larger pool, letting the ranking find peers with similar scale (a proxy for risk and diversification) and similar margin structure. The harmonic mean is the theoretically preferred aggregator for price multiples because it averages the inverse (yield), dampening the pull of a few very high-multiple peers.
  [g01-03] EV/EBITDA median 0.341 | mean 0.514 | coverage 100.0% | beats industry 3/4 yrs | gain vs industry -0.001
      EV/EBITDA | rank gross_margin 1, capex_intensity 1, asset_turnover 0.5, sales_growth_1y 1, log_sales 0.5 | k=15, median, min_peers=3
      mechanism: Firms with similar cost structure (gross margin, capital intensity, asset turnover) and growth face similar reinvestment needs and margin durability, so they should command similar EBITDA multiples even when their SIC codes differ. Ignoring SIC codes tests whether economic similarity beats coarse industry labels, which are often stale for diversified firms.
  [g02-03] EV/Sales median 0.398 | mean 0.658 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.287
      EV/Sales | screen same industry_l3, band ebitda_margin±0.05 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 1, gross_margin 0.5 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.05] -> [same industry_l2] -> []
      mechanism: Within a 3-digit industry, peers share closer business models and risk than within a 2-digit group; adding the EBITDA margin band then fixes the profitability term. Gross margin in the ranking captures pricing power and operating leverage, which shape how durable the current EBITDA margin is.
  [g02-01] EV/Sales median 0.409 | mean 0.664 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.282
      EV/Sales | screen same industry_l2, band ebitda_margin±0.03 | rank ebitda_margin 2, sales_growth_1y 1, log_sales 1 | k=8, median, min_peers=4 | fallback [same industry_l2, band ebitda_margin±0.05] -> [band ebitda_margin±0.03] -> [band ebitda_margin±0.05] -> [same industry_l2] -> []
      mechanism: EV/Sales is EV/EBITDA times EBITDA margin, so the margin term dominates sales-multiple dispersion; g01-06 showed a +/-0.05 margin band inside the 2-digit industry removes most of it. Tightening the band to +/-0.03 and still ranking on margin should cancel more of the margin term, with a cascade of wider bands so thin industries keep margin-matched peers instead of falling back to unmatched industry members.
  [g01-06] EV/Sales median 0.412 | mean 0.662 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.284
      EV/Sales | screen same industry_l2, band ebitda_margin±0.05 | rank sales_growth_1y 1, log_sales 1, ebitda_margin 1 | k=8, median, min_peers=4 | fallback [band ebitda_margin±0.05] -> [same industry_l2] -> []
      mechanism: A hard EBITDA-margin band inside the 2-digit industry guarantees that peers share a similar conversion of sales into cash earnings, the main determinant of EV/Sales, while the industry screen keeps common risk and growth outlook. Ranking the survivors on growth and size then refines for the remaining value drivers.
  [g02-02] EV/Sales median 0.430 | mean 0.636 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.310
      EV/Sales | screen band ebitda_margin±0.04, band sales_growth_1y±0.1 | rank ebitda_margin 2, sales_growth_1y 1, roic 1, log_sales 0.5 | k=10, median, min_peers=5 | fallback [band ebitda_margin±0.04] -> [band ebitda_margin±0.08] -> []
      mechanism: If EV/Sales is governed by cash margin and growth, firms matched on both within hard bands should share the multiple regardless of SIC code. Ranking the survivors on ROIC and size then adjusts for reinvestment efficiency and risk; this tests whether the industry screen in g01-06 adds anything beyond the margin match.
  [g01-05] EV/Sales median 0.538 | mean 0.767 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.179
      EV/Sales | rank ebitda_margin 3, gross_margin 1, sales_growth_1y 1, roic 1 | k=15, median, min_peers=3
      mechanism: If EV/Sales is mostly a function of margin, growth and return on capital, then the closest firms on those drivers anywhere in the economy should be better comparables than industry members with very different profitability. Gross margin adds information on pricing power and the scalability of the cost base.
  [g01-04] EV/Sales median 0.554 | mean 0.817 | coverage 100.0% | beats industry 4/4 yrs | gain vs industry +0.128
      EV/Sales | screen same industry_l3 | rank ebitda_margin 3, sales_growth_1y 1, log_sales 0.5 | k=8, median, min_peers=5 | fallback [same industry_l2] -> []
      mechanism: EV/Sales equals EV/EBITDA times EBITDA margin, so most cross-sectional variation in sales multiples comes from profitability. Matching industry peers primarily on EBITDA margin, then growth, should cancel the margin term that makes plain industry EV/Sales medians so noisy.

FAILED OR REJECTED ATTEMPTS (most recent)
  (none)

Each proposal needs:
  - "mechanism": the economic reason these peers should share this firm's multiple (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "beats the industry median in at least 3 of 4 years"
  - "recipe": the recipe object

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "recipe": {"multiple": "...", "filters": [...], "rank": {...}, "k": 8, "agg": "median", "min_peers": 3, "fallback": [...]}}]}
