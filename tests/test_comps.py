"""Unit tests for the comps engine, validator and grader.

Run from the valuation-lab folder:  python3 -m unittest discover -s tests -v
"""

import unittest

import numpy as np
import pandas as pd

from valuationlab.baselines import baselines_for
from valuationlab.engine import apply_recipe
from valuationlab.grader import Protocol, compare, estimate, summarize
from valuationlab.panel import build_panel
from valuationlab.recipe import RecipeError, validate
from valuationlab.synthetic import generate


def tiny_panel() -> pd.DataFrame:
    """Five firms in one year; EV/EBITDA multiples 6, 8, 10, 12, 30."""
    mults = [6, 8, 10, 12, 30]
    rows = []
    for i, m in enumerate(mults):
        rows.append(dict(
            id=f"A{i}", fiscal_year=2015,
            industry_l2="Tech" if i < 4 else "Energy",
            industry_l3="Tech-1" if i < 4 else "Energy-1",
            sales=100.0, ebitda=10.0, ebit=8.0, net_income=5.0, book_equity=50.0,
            total_debt=0.0, cash=0.0, mkt_cap=10.0 * m, total_assets=60.0,
            gross_profit=40.0, minority_interest=0.0,
        ))
    return build_panel(pd.DataFrame(rows))


class EngineTests(unittest.TestCase):
    def test_market_median_excludes_target(self):
        recipe = validate({"name": "mkt", "multiple": "EV/EBITDA", "k": "all", "agg": "median"})
        est = apply_recipe(tiny_panel(), recipe, keep_peers=True).set_index("id")
        # A0's peers are A1..A4 (8, 10, 12, 30): median 11 -> estimate 110.
        self.assertAlmostEqual(est.loc["A0", "estimate"], 110.0)
        self.assertNotIn("A0", est.loc["A0", "peers"])
        for fid, peers in est["peers"].items():
            self.assertNotIn(fid, peers)

    def test_industry_filter_and_fallback(self):
        recipe = validate({
            "name": "ind", "multiple": "EV/EBITDA", "filters": [{"same": "industry_l3"}],
            "k": "all", "min_peers": 2, "fallback": [[]],
        })
        est = apply_recipe(tiny_panel(), recipe).set_index("id")
        # A0's industry peers: A1..A3 (8, 10, 12) -> median 10 -> 100, primary filters.
        self.assertAlmostEqual(est.loc["A0", "estimate"], 100.0)
        self.assertEqual(est.loc["A0", "fallback_level"], 0)
        # A4 is alone in Energy, so it falls back to the whole market.
        self.assertEqual(est.loc["A4", "fallback_level"], 1)

    def test_no_peers_gives_missing_estimate(self):
        recipe = validate({"name": "ind", "multiple": "EV/EBITDA",
                           "filters": [{"same": "industry_l3"}], "k": "all", "min_peers": 2})
        est = apply_recipe(tiny_panel(), recipe).set_index("id")
        self.assertTrue(np.isnan(est.loc["A4", "estimate"]))
        self.assertEqual(est.loc["A4", "fallback_level"], -1)

    def test_harmonic_mean(self):
        recipe = validate({"name": "h", "multiple": "EV/EBITDA", "k": "all", "agg": "harmonic_mean"})
        est = apply_recipe(tiny_panel(), recipe).set_index("id")
        expected = 4 / (1 / 8 + 1 / 10 + 1 / 12 + 1 / 30) * 10
        self.assertAlmostEqual(est.loc["A0", "estimate"], expected)


    def test_estimate_cache_keys_on_definition_not_name(self):
        """Two different recipes with the same name must not share cached estimates."""
        panel = tiny_panel()
        a = validate({"name": "same", "multiple": "EV/EBITDA", "k": "all", "agg": "median"})
        b = validate({"name": "same", "multiple": "EV/EBITDA", "k": "all", "agg": "harmonic_mean"})
        ea = estimate(panel, a, [2015]).set_index("id")
        eb = estimate(panel, b, [2015]).set_index("id")
        self.assertAlmostEqual(ea.loc["A0", "estimate"], 110.0)
        self.assertAlmostEqual(eb.loc["A0", "estimate"], 4 / (1 / 8 + 1 / 10 + 1 / 12 + 1 / 30) * 10)


class PanelTests(unittest.TestCase):
    def test_sic_only_data_gets_industry_levels(self):
        raw = pd.DataFrame([dict(
            id="S1", fiscal_year=2015, sic=3674, sales=100.0, ebitda=10.0, ebit=8.0,
            net_income=5.0, book_equity=50.0, total_debt=0.0, cash=0.0, mkt_cap=100.0,
        )])
        panel = build_panel(raw)
        row = panel.iloc[0]
        self.assertEqual((row["industry_l2"], row["industry_l3"], row["industry_l4"]), ("36", "367", "3674"))


class FactSetReaderTests(unittest.TestCase):
    def test_reads_export_layout_and_applies_filters(self):
        import tempfile
        from pathlib import Path
        from valuationlab.factset import read_export

        header = ["Symbol", "Name", "Net Sales", "MktVal Co", "Fiscal Period End Date", "SIC Code", "Entity ID", "Sec Type"]
        rows = [
            ["FactSet Universal Screening"] + [None] * 7, [None] * 8, header, [None] * 8,
            ["AAA", "Keep Co", 500, 900, "12/31/2023", "3674", "E1", "SHARE"],
            ["BBB", "ADR Co", 500, 900, "12/31/2023", "3674", "E2", "ADR"],
            ["CCC", "Bank Co", 500, 900, "12/31/2023", "6021", "E3", "SHARE"],
            ["DDD", "Tiny Co", 5, 20, "12/31/2023", "3674", "E4", "SHARE"],
            ["EEE", "Stale Co", 500, 900, "12/31/2020", "3674", "E5", "SHARE"],
            ["FFF", "Empty Co", "#N/A", "#N/A", "@NA", "3674", "E6", "SHARE"],
        ]
        cmap = {"Symbol": "ticker", "Name": "name", "Net Sales": "sales", "MktVal Co": "mkt_cap",
                "Fiscal Period End Date": "fye_date", "SIC Code": "sic", "Entity ID": "id", "Sec Type": "sec_type"}
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "factset_2024.xlsx"
            pd.DataFrame(rows).to_excel(path, header=False, index=False)
            df, log = read_export(path, cmap)
        self.assertEqual(df["ticker"].tolist(), ["AAA"])
        self.assertEqual(df["fiscal_year"].iloc[0], 2023)       # June 30, 2024 snapshot -> FY2023
        self.assertEqual(log["value_date"], "2024-06-30")       # inferred from the file name


class ValidatorTests(unittest.TestCase):
    def test_rejects_market_based_feature(self):
        with self.assertRaises(RecipeError) as ctx:
            validate({"name": "x", "multiple": "EV/EBITDA", "rank": {"mkt_cap": 1.0}, "k": 5})
        self.assertIn("market-based", str(ctx.exception))

    def test_fixed_k_requires_rank(self):
        with self.assertRaises(RecipeError):
            validate({"name": "x", "multiple": "EV/EBITDA", "k": 5})

    def test_reports_all_problems(self):
        with self.assertRaises(RecipeError) as ctx:
            validate({"name": "", "multiple": "EV/Foo", "agg": "mode"})
        msg = str(ctx.exception)
        for part in ("name", "multiple", "agg"):
            self.assertIn(part, msg)


class GraderTests(unittest.TestCase):
    def test_holdout_is_sealed(self):
        p = Protocol(explore=(2010,), validate=(2011,), holdout=(2012,))
        with self.assertRaises(PermissionError):
            p.years("holdout")
        self.assertEqual(p.years("holdout", allow_holdout=True), [2012])

    def test_recovers_synthetic_structure(self):
        panel = build_panel(generate(n_firms=500, seed=3))
        years = list(range(2010, 2017))
        base = baselines_for("EV/EBITDA")
        mkt = apply_recipe(panel, base["market_median"], years)
        ind = apply_recipe(panel, base["industry_median"], years)
        smart = apply_recipe(panel, validate({
            "name": "growth+roic", "multiple": "EV/EBITDA",
            "filters": [{"same": "industry_l3"}],
            "rank": {"sales_growth_3y": 0.6, "roic": 0.4}, "k": 8,
            "fallback": [[{"same": "industry_l2"}]],
        }), years)
        # Industry peers beat the market median; matching on the true drivers beats both.
        self.assertLess(summarize(ind)["median_abs_error"], summarize(mkt)["median_abs_error"])
        self.assertGreater(compare(smart, ind)["mean_gain"], 0)


if __name__ == "__main__":
    unittest.main()
