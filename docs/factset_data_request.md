# FactSet Data Request — Comps Module (v1)

This file lists the data the comps engine needs. One row = one company × one fiscal year.
Excel (.xlsx) or CSV exports both work. Column names do not need to match exactly;
`config/factset_columns.json` maps FactSet headers to the engine's internal names.

## 1. Universe

| Item | Specification |
| --- | --- |
| Region | U.S.-listed common equity (NYSE, Nasdaq, NYSE American) |
| Exclusions | Financials (banks, insurance, REITs, diversified financials). ADRs, ETFs, funds, SPACs if easy to filter |
| Period | Fiscal years 2005–2024 (longer is better; 2000+ if available) |
| **Inactive companies** | **Include delisted / acquired / bankrupt companies.** A universe of today's survivors biases every result |
| Currency | USD |
| Frequency | Annual (fiscal year) |

## 2. Fields per company-year

### Identifiers and classification

| Internal name | Description | Required |
| --- | --- | --- |
| `id` | FactSet entity or security ID (stable over time) | yes |
| `ticker` | Ticker at the time (or latest) | yes |
| `name` | Company name | yes |
| `fiscal_year` | Fiscal year label | yes |
| `fye_date` | Fiscal year-end date | yes |
| `rbics_l1` … `rbics_l4` | FactSet RBICS industry levels (sector → sub-industry) | yes (at least L2 and L3) |
| `gics_sector`, `gics_industry` | GICS classification | optional |
| `sic` | SIC code | optional |

### Financial statement items (fiscal year, USD millions)

| Internal name | Description | Required |
| --- | --- | --- |
| `sales` | Net sales / revenue | yes |
| `gross_profit` | Gross income | yes |
| `ebitda` | EBITDA (operating) | yes |
| `ebit` | EBIT / operating income | yes |
| `net_income` | Net income (to common) | yes |
| `total_assets` | Total assets | yes |
| `book_equity` | Total common equity | yes |
| `total_debt` | Total debt (short + long term) | yes |
| `cash` | Cash and short-term investments | yes |
| `minority_interest` | Non-controlling interest | yes |
| `preferred` | Preferred stock | optional |
| `rnd` | R&D expense | optional |
| `capex` | Capital expenditures | optional |
| `dividends` | Common dividends paid | optional |

### Market data — measured at the valuation date

**Valuation date rule:** the June 30 that comes at least 3 months after fiscal year-end.
Example: FY ending Dec 2023 → June 30, 2024. FY ending Sep 2023 → June 30, 2024.
(If this is hard to pull, send month-end values for every month and the code will pick the date.)

| Internal name | Description | Required |
| --- | --- | --- |
| `value_date` | Date the market values below refer to | yes |
| `price` | Share price | yes |
| `shares` | Shares outstanding | yes |
| `mkt_cap` | Market capitalization (USD millions) | yes |
| `ev` | Enterprise value (USD millions), if FactSet provides it | optional (computed otherwise) |

### Analyst consensus (optional, enables forward multiples)

| Internal name | Description |
| --- | --- |
| `eps_fy1` | Consensus EPS for the next fiscal year, as of the valuation date |
| `ebitda_fy1` | Consensus EBITDA for the next fiscal year, as of the valuation date |
| `sales_fy1` | Consensus sales for the next fiscal year, as of the valuation date |

## 3. Practical notes

- **Point-in-time:** if FactSet offers "as originally reported" values, prefer them. Otherwise note that values may include later restatements.
- **Size:** about 3,000–4,000 companies per year × 20 years ≈ 70,000 rows. If the export limit is lower, split by year or sector into several files; the loader stacks them.
- **Before the full pull:** send a screenshot of the export screen or a 50-row sample first so the column mapping can be checked.
