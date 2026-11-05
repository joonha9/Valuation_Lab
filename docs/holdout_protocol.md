# Holdout evaluation protocol (FY2024–2025)

Status: **frozen before the holdout was opened.** This file, `results/holdout/manifest.json` and
`scripts/holdout_eval.py` are committed together before any recipe is scored on FY2024 or FY2025.
The manifest stores this file's SHA-256, and the evaluation script refuses to run if the file has
changed since.

## 1. Purpose

Every result reported so far uses the validation years FY2020–2023. Finalists were chosen on the
exploration years FY2016–2019 by a fixed rule and scored on the validation years once. The holdout
years FY2024–2025 have never been loaded by any script that scores recipes. This evaluation scores
the frozen finalists on those two years, once, to test whether the validation findings hold on
later years that played no part in proposing, selecting or reporting any recipe.

## 2. Data

- Files: `data/holdout/factset_2025.xlsx` (FY2024 statements, market value at June 30, 2025) and
  `data/holdout/factset_2026.xlsx` (FY2025 statements, market value at June 30, 2026). They were
  exported with the same FactSet screen as the earlier files.
- Pre-opening checks (no recipe scored): `scripts/check_exports.py data/raw data/holdout` passed on
  2026-11-05 for all 11 files. Fiscal year-ends center on the expected year, and no value column is
  identical across any pair of files, so no column was left on another year's setting.
- Sample rules are unchanged: ordinary shares, non-financial firms (SIC 6000–6999 dropped), market
  value of at least $100M, statements no more than 18 months old. Features are built by the same
  code. Ratio features are winsorized within each fiscal year, and lags use exact prior years, so
  adding the holdout rows cannot change any earlier firm-year.
- **Integrity gate.** Before scoring the holdout, the script rebuilds the panel with the holdout
  files included and re-scores every recipe in the manifest on the validation years. Every
  validation median |error|, mean |error| and coverage must equal the stored value (tolerance
  1e-9). If any value differs, the script stops before scoring the holdout and writes only the
  mismatches.

## 3. What is scored (fixed in `results/holdout/manifest.json`)

All recipes enter exactly as frozen in their run's `final.json`. Nothing is re-selected, re-tuned
or added after this protocol is committed.

| Role | Recipes | Source |
|---|---|---|
| Primary: agent finalists | 10 (runs r1–r5 × EV/EBITDA, EV/Sales) | `results/agent_runs/r*/final.json` |
| Secondary: ablation finalists | 30 (nc1–5, na1–5, nn1–5 × 2 multiples; some share a definition) | same |
| Random-search finalists | 2 (random-075, random-188) | r1 `final.json` |
| Random-search pool | 200 random recipes (100 per multiple), used only for the luck distribution | r1 `archive_random.jsonl` |
| Hand-written recipes | 3 | `recipes/examples.json` |
| Baselines | market median, industry median (SIC3, fallback SIC2), Bhojraj–Lee regression, Bhojraj–Lee peers | `valuationlab/baselines.py` |

Bhojraj–Lee coefficients for FY2024 come from FY2023 and for FY2025 from FY2024, as in every other
year. Recipes with identical definitions are scored once and shared.

## 4. Primary analysis

The primary analysis repeats the headline table in the README on FY2024–2025. The metric is the
median |ln(V_est / V)| over the pooled holdout firm-years (lower is better), computed for each
multiple separately.

For each multiple (EV/EBITDA, EV/Sales):

- **H1. Agents vs industry median.** In how many of the 5 full runs is the finalist's holdout error
  below the industry median's? One-sided sign test (5 of 5 gives p = 0.031).
- **H2. Agents vs Bhojraj–Lee regression.** The same sign test.
- **H3. Agents vs random search with the same budget.** The procedure of
  `scripts/multi_run_analysis.py`, with holdout errors in place of validation errors. For each run,
  draw as many recipes from the 100 random recipes of that multiple as the run graded, apply the same
  selection rule on exploration scores, and record the selected recipe's holdout error. Average the
  five simulated runs. Repeat 20,000 times (seed 2026). The one-sided p-value is the share of
  simulated averages at or below the agents' mean holdout error.
- **H4. Agents vs the hand-written recipe** used in the README table ("Growth and ROIC peers" for
  EV/EBITDA, "Margin-matched sales peers" for EV/Sales). The same sign test. In validation this held
  for EV/Sales (5 of 5) but was a tie for EV/EBITDA (3 of 5), so H4 for EV/EBITDA is not expected to
  hold.

**Expectations from years already seen.** The dry run (Section 8) scores everything on FY2022–2023,
the last two validation years, which were already reported. There, EV/Sales passes H1–H3 clearly.
For EV/EBITDA the industry median's error fell to 0.401, and the agents beat it in only 3 of 5 runs
(mean 0.393), so H1 for EV/EBITDA may well fail on the holdout. This is written down before opening
so that such a failure is not read as a surprise, and a pass is not overstated.

**Reading the result.** The validation finding "agents beat the standard methods out of sample"
counts as **replicated** for a multiple if H1, H2 and H3 all hold at the 5% level. It counts as
**partly replicated** if the direction holds for all three (agents' mean error lower) but at least
one test misses 5%, and as **not replicated** otherwise. The result is reported whichever way it
falls. Both multiples are reported, and no single favourable test is singled out.

## 5. Secondary analyses (descriptive or exploratory)

- **S1. Ablation.** The four conditions (full, no critic, no archive, neither) on the holdout years:
  each condition's mean holdout error, its relative improvement over the industry median, its
  p-value against random search, and exact permutation tests against the full condition, as in
  `scripts/ablation_analysis.py`. In validation no condition differed from the full one, and the
  same is expected here.
- **S2. Decay.** For every recipe and baseline, the change in median |error| from validation to
  holdout, and the agents' relative improvement over the industry median in each period. This
  separates market-wide shifts in error (which move every method) from a loss of the agents'
  advantage.
- **S3. By year.** FY2024 and FY2025 separately: each recipe's median |error| and whether it beats the
  industry median and Bhojraj–Lee in each year.
- **S4. Firm level.** For each agent finalist, the share of commonly covered firm-years where it is
  closer than the industry median, and the mean gain in |error|.
- Coverage, the share of estimates within 15% of market value, and the fallback share are reported
  for every recipe.

## 6. Limits stated in advance

- Two holdout years are few. The year-clustered Newey–West t-statistic is not computed (it needs at
  least 6 yearly means), and none was computed for the four validation years either. The tests in
  H1–H4 treat the search run as the unit. They ask whether the search procedure reliably finds
  rules that beat the benchmarks on these two years. They do not establish stability across many
  market regimes.
- The five full runs use the same model and the same brief, so they are not independent of the
  model's prior knowledge; the ablation already suggested that this prior knowledge drives most of
  the gain.
- FY2025 market values are as of June 30, 2026, which is recent. If FactSet later revises
  statements for FY2025, the panel could change slightly; the file used here is the one exported on
  2026-11-02.

## 7. Rules after opening

- The script runs once. It writes `results/holdout/holdout_results.json` and refuses to run again
  if that file exists.
- If a bug is found after opening, the original output is kept, the fix is committed separately,
  and both results are reported with the reason (a deviation note in this file and in the README).
- Holdout scores are never used to select, revise or rank recipes. After this evaluation the
  holdout is spent: later studies (longer searches, other models, Leadership Lab) keep selecting
  and reporting on the validation years, and a new untouched test needs FY2026 data (market values
  at June 30, 2027).
- Leadership Lab draws are not scored on the holdout under this protocol.

## 8. Commands

```bash
python3 scripts/holdout_eval.py manifest   # freeze the recipe list and this file's hash
python3 scripts/holdout_eval.py dry-run    # full pipeline on the validation panel, FY2022–2023 standing in for the holdout
python3 scripts/holdout_eval.py open       # the one real evaluation
```

The dry run never reads `data/holdout/`. It only checks that the code runs end to end and that the
integrity gate passes. It ran on 2026-11-05: all 243 validation scores were reproduced exactly, and
its output is kept in `results/holdout/dry_run/`.
