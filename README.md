# ValuationLab

**Which companies are really comparable?** ValuationLab is a test bench for comparable-company
valuation ("comps"). It turns peer selection into explicit, firm-agnostic rules ("recipes"),
grades every rule on 27,693 US firm-years, and lets AI agents propose and test rules
themselves.

**Project site:** https://joonha9.github.io/Valuation_Lab/ (English / 한국어). The site is plain
HTML, CSS and JavaScript, generated from the results by `scripts/build_site.py`.

## Findings (validation years FY2020–2023, median |ln(V_est / V)|, lower is better)

| Method | EV/EBITDA | EV/Sales |
|---|---|---|
| AI agents, mean of 5 independent runs | **0.399** | **0.502** |
| Random search, same budget and selection rule (mean of 5) | 0.411 | 0.584 |
| Hand-written recipe | 0.405 | 0.605 |
| Industry median (3-digit SIC) | 0.426 | 0.650 |
| Bhojraj–Lee (2002) warranted-multiple regression | 0.469 | 0.751 |

- Agents beat random search with the same budget on both multiples (p < 0.001), and beat the
  industry median and Bhojraj–Lee in 5 of 5 runs.
- Ablation (20 runs): removing the referee, the archive, or both did not hurt. At 30 proposals
  per run, the gain comes from the proposer's prior knowledge, not from the feedback loop.
- These are four validation years from one model; the FY2024–2025 holdout is still sealed.

## How it works

1. **Data.** Annual FactSet snapshots of US-listed, non-financial firms with market value of at
   least $100M. Statements for fiscal year *t* are paired with market value on June 30 of *t+1*.
   Since-delisted firms are kept, so the sample is not limited to survivors.
2. **Recipes.** A recipe screens candidate peers (same SIC group, bands on characteristics),
   ranks them by distance on standardized accounting features, keeps the *k* nearest, and
   applies their median multiple to the target's EBITDA or sales.
3. **Grading.** A deterministic grader scores recipes against practitioner baselines and an
   academic benchmark (Bhojraj & Lee 2002, with prior-year coefficients).
4. **Protocol.** Explore FY2016–2019, validate FY2020–2023, holdout FY2024–2025 (sealed).
   Finalists are picked by a rule fixed before the search, then graded on validation years once.
5. **Agents.** Following the SignalLab design (Liu, Liu, Liu & Mei 2026), a proposer agent writes
   recipes with a mechanism and a falsifiable prediction. A separate referee agent, which sees
   no scores, approves or rejects each one. Every attempt is archived, so the search
   denominator is known. Agents ran as Claude Code subagents.

## Corrections

- **2026-11-04, estimate cache.** The grader cached estimates by recipe *name*, so a recipe that
  reused an earlier recipe's name in the same process received that recipe's estimates. Re-grading
  every archived recipe found 16 of 4,492 exploration scores affected, in runs na2–na5, nc4,
  nn2–nn5, r3 and r5. The cache now keys on the full recipe definition (with a regression test), and
  the 16 records were re-graded in place (the old score is kept as `explore_before_cache_fix`).
  No finalist changed, every validation score in `final.json` was confirmed, and the multi-run
  results are unchanged. In the ablation, two runs (na5, nn5) have one fewer eligible recipe.
  Proposers in r3, r5 and nc4 saw a wrong score for one recipe in their archive feedback; those
  searches are kept as they ran.

## Rules the code enforces

- A firm is never its own peer, and its own market value is never an input.
- Benchmark regressions use only the prior fiscal year.
- Holdout years refuse to load unless explicitly unlocked.
- Every data export is checked for date alignment (`scripts/check_exports.py`), including a test
  for columns stuck on a single fiscal year. That test caught a look-ahead error in the first
  exports.

## Repository layout

```text
valuationlab/       panel, recipe validator, comps engine, grader, Bhojraj–Lee benchmark, agent loop
scripts/            check_exports, run_comps, agent_loop / agent_batch, multi_run and ablation analysis, build_site
recipes/            hand-written example recipes
results/agent_runs/ every agent run: prompts, replies, archives, frozen finalists, summaries
site/               page template (HTML/CSS/JS) and generated page
docs/index.html     standalone copy of the site, served by GitHub Pages
tests/              unit tests (python3 -m unittest discover -s tests)
```

## Reproducing

The FactSet data is licensed and **not included**. With your own exports in `data/raw/`
(`factset_YYYY.xlsx`, one per year; see `docs/factset_data_request.md`):

```bash
python3 scripts/check_exports.py                 # validate the exports
python3 scripts/run_comps.py --data data/raw/factset_20*.xlsx --explore 2016-2019 --validate 2020-2023 --holdout 2024-2025
python3 scripts/agent_loop.py init --run r1      # then prompt / submit / grade / finalize
python3 scripts/multi_run_analysis.py --runs r1 r2 r3 r4 r5
python3 scripts/ablation_analysis.py
python3 scripts/build_site.py                    # rebuild site/index.html and docs/index.html
```

Requires Python 3.11+, pandas, numpy and openpyxl.

## References

- Liu, Liu, Liu & Mei (2026). "Can AI Do Financial Research?" Working paper.
- Bhojraj, S. & Lee, C. M. C. (2002). "Who Is My Peer? A Valuation-Based Approach to the Selection of Comparable Firms." *Journal of Accounting Research* 40(2).
- Alford, A. W. (1992). "The Effect of the Set of Comparable Firms on the Accuracy of the Price-Earnings Valuation Method." *Journal of Accounting Research* 30(1).
- Liu, J., Nissim, D. & Thomas, J. (2002). "Equity Valuation Using Multiples." *Journal of Accounting Research* 40(1).

Author: Joonha
