# Holdout evaluation, FY2024–2025

Run once on 2026-11-05 under [`docs/holdout_protocol.md`](../../docs/holdout_protocol.md), which was
frozen and pushed before opening (commit `38760bb`). The integrity gate passed: with the holdout
files added to the panel, all 243 stored validation scores were reproduced exactly. Full output:
[`holdout_results.json`](holdout_results.json). No deviations from the protocol.

## Verdict

**Replicated for both multiples.** H1, H2 and H3 hold at the 5% level for EV/EBITDA and for EV/Sales.
The finalists of all five agent runs beat the industry median, the Bhojraj–Lee regression and the
random-search finalist on years that played no part in proposing, selecting or reporting any recipe.

## Primary results (median |ln(V_est / V)|, pooled FY2024–2025, lower is better)

| Method | EV/EBITDA validation | EV/EBITDA holdout | EV/Sales validation | EV/Sales holdout |
|---|---|---|---|---|
| AI agents, mean of 5 runs | 0.399 | **0.402** | 0.502 | **0.496** |
| Random search, same budget (median of simulated means) | — | 0.423 | — | 0.581 |
| Random-search finalist (fixed) | 0.400 | 0.420 | 0.555 | 0.541 |
| Hand-written recipe (README table) | 0.405 | 0.414 | 0.605 | 0.622 |
| Industry median (SIC3, fallback SIC2) | 0.426 | 0.445 | 0.650 | 0.660 |
| Bhojraj–Lee regression | 0.469 | 0.444 | 0.751 | 0.692 |
| Bhojraj–Lee peers | 0.478 | 0.469 | 0.763 | 0.729 |
| Market median | 0.481 | 0.465 | 0.826 | 0.801 |

| Test | EV/EBITDA | EV/Sales |
|---|---|---|
| H1 vs industry median (runs better, sign p) | 5/5, p = 0.031 | 5/5, p = 0.031 |
| H2 vs Bhojraj–Lee regression | 5/5, p = 0.031 | 5/5, p = 0.031 |
| H3 vs random search, same budget (20,000 simulations) | p < 0.0001 (null 5–95%: 0.416–0.437) | p < 0.0001 (null 5–95%: 0.554–0.609) |
| H4 vs hand-written recipe | 5/5, p = 0.031 | 5/5, p = 0.031 |

Per run (validation → holdout):

| Run | EV/EBITDA | EV/Sales |
|---|---|---|
| r1 | 0.394 → 0.403 | 0.489 → 0.527 |
| r2 | 0.398 → 0.402 | 0.526 → 0.500 |
| r3 | 0.406 → 0.408 | 0.511 → 0.489 |
| r4 | 0.388 → 0.397 | 0.469 → 0.470 |
| r5 | 0.411 → 0.397 | 0.512 → 0.494 |

## Against the expectation written before opening

The protocol expected that H1 for EV/EBITDA might fail, because in FY2022–2023 the industry median's
error had fallen to 0.401 and the agents beat it in only 3 of 5 runs. On the holdout the industry
median's error rose again (0.452 in FY2024, 0.437 in FY2025), while the agents' error stayed close
to its validation level (0.396–0.408). The narrow margin in FY2022–2023 was therefore a dip in the
benchmark's error, not a loss of the agents' edge. H4 for EV/EBITDA, expected to be a tie, also held
(5 of 5), because the hand recipe's error rose by 0.009.

## Secondary results

**S2. Decay.** The agents' error barely moved (EV/EBITDA +0.002, EV/Sales −0.006). Their relative
improvement over the industry median grew from 6.3% to 9.8% (EV/EBITDA) and from 22.9% to 24.8%
(EV/Sales), mostly because the industry median got worse. The Bhojraj–Lee regression improved
(−0.025 and −0.059) and is close to the industry median for EV/EBITDA on the holdout (0.444 vs
0.445), but it stays well behind the agents.

**S3. By year.** Every agent finalist beats the industry median in both holdout years on both
multiples. Against the Bhojraj–Lee regression, measured by the yearly mean gain in |error| that the
grader uses for year counts, the EV/Sales finalists win both years. For EV/EBITDA four of five
finalists win only one of the two years, although all five have the lower pooled median error. Over both years the
mean gain over Bhojraj–Lee on EV/EBITDA is positive but small (0.002–0.013 in |error|, against
0.08–0.17 on EV/Sales), so on EV/EBITDA the agents' lead over Bhojraj–Lee is real in the median but
thin.

**S4. Firm level.** Against the industry median on commonly covered firm-years:

| Run | EV/EBITDA share closer | EV/EBITDA mean gain | EV/Sales share closer | EV/Sales mean gain |
|---|---|---|---|---|
| r1 | 45.6% | 0.039 | 59.6% | 0.247 |
| r2 | 51.9% | 0.038 | 59.3% | 0.274 |
| r3 | 54.3% | 0.050 | 59.3% | 0.247 |
| r4 | 52.7% | 0.047 | 61.0% | 0.276 |
| r5 | 53.2% | 0.046 | 59.3% | 0.190 |

On EV/Sales the agents' recipes are closer for about 60% of firm-years. On EV/EBITDA the edge is thin
firm by firm (46–54%): the gain comes from avoiding large misses, not from being closer for most
firms. Coverage is 98–100% for every finalist. The share of estimates within 15% of market value is
21% (EV/EBITDA) and 16–19% (EV/Sales).

**S1. Ablation** (mean relative improvement over the industry median, averaged over the two
multiples):

| Condition | Validation | Holdout |
|---|---|---|
| Full (proposer + archive + critic) | 14.6% | 17.3% |
| No critic | 16.9% | 20.1% |
| No archive | 14.1% | 17.0% |
| Neither | 15.0% | 17.6% |

As in validation, removing the archive or the critic does not hurt. The no-critic condition is again
the best, now with an exact permutation p = 0.008 in its favour against the full condition
(validation: p = 0.06). This test is secondary and exploratory, one of three comparisons with the
full condition. It is consistent with the earlier reading that at a 30-proposal budget the critic
mainly uses up proposals, but it is not a confirmatory result.

## Limits

Two holdout years, one model, one brief. The tests treat the search run as the unit, so they show
that the search procedure reliably finds rules that beat the benchmarks on these two years. They do
not establish stability across many market regimes. The holdout is now spent. Later studies keep
selecting and reporting on the validation years, and the next untouched test needs FY2026 data
(market values at June 30, 2027).
