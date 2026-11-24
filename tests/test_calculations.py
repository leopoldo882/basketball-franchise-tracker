"""Checks on the calculations the numbers depend on, using small made-up inputs
where the right answer is easy to work out by hand.

Run from the project folder:  python -m unittest discover -s tests
"""

import math
import unittest

import pandas as pd

from analysis import cross_checks, listed_index, multiples_cross_league, nba_growth, risk_return
from collectors import basketnews_budgets


class ParseAmountTest(unittest.TestCase):
    def test_single_figure(self):
        self.assertEqual(basketnews_budgets.parse_amount("€45M"), (45.0, 45.0))

    def test_range(self):
        self.assertEqual(basketnews_budgets.parse_amount("€26.5-27.0M"), (26.5, 27.0))

    def test_comma_decimal(self):
        self.assertEqual(basketnews_budgets.parse_amount("€8,5M"), (8.5, 8.5))

    def test_missing_figure(self):
        self.assertIsNone(basketnews_budgets.parse_amount("-"))


class GrowthTest(unittest.TestCase):
    def test_cagr(self):
        # 100 -> 121 over two years is 10% a year
        self.assertAlmostEqual(nba_growth.cagr(100, 121, 2), 0.10)

    def test_years_between_uses_months(self):
        # Feb 2019 to Oct 2021 is 32 months, not 3 years
        self.assertAlmostEqual(nba_growth.years_between("2019-02", "2021-10"), 32 / 12)


class IndexTest(unittest.TestCase):
    def test_equal_weight_ignores_missing_members(self):
        returns = pd.DataFrame({"A": [0.10, 0.20], "B": [None, 0.00]})
        index_return, members = listed_index.equal_weight_returns(returns, ["A", "B"])
        self.assertAlmostEqual(index_return.iloc[0], 0.10)   # only A traded
        self.assertAlmostEqual(index_return.iloc[1], 0.10)   # (0.20 + 0.00) / 2
        self.assertEqual(list(members), [1, 2])

    def test_require_all_drops_incomplete_months(self):
        returns = pd.DataFrame({"A": [0.10, 0.20], "B": [None, 0.00]})
        index_return, _ = listed_index.equal_weight_returns(returns, ["A", "B"], require_all=True)
        self.assertEqual(len(index_return), 1)

    def test_drawdown(self):
        level = listed_index.to_level(pd.Series([0.10, -0.50, 0.20]))
        self.assertAlmostEqual(listed_index.max_drawdown(level), -0.50)


class RiskTest(unittest.TestCase):
    def test_first_month_fall_counts_as_drawdown(self):
        self.assertAlmostEqual(risk_return.max_drawdown(pd.Series([-0.10, 0.05])), -0.10)

    def test_beta(self):
        market = pd.Series([0.01, -0.02, 0.03, 0.00])
        self.assertAlmostEqual(risk_return.beta(market, market), 1.0)
        self.assertAlmostEqual(risk_return.beta(2 * market, market), 2.0)

    def test_volatility_is_annualised(self):
        returns = pd.Series([0.01, -0.01, 0.01, -0.01])
        self.assertAlmostEqual(risk_return.annual_volatility(returns), returns.std() * math.sqrt(12))

    def test_sharpe_subtracts_risk_free(self):
        returns = pd.Series([0.02, 0.00, 0.02, 0.00])
        risk_free = pd.Series([0.01, 0.01, 0.01, 0.01])
        # average excess return is zero, so the Sharpe ratio is zero
        self.assertAlmostEqual(risk_return.sharpe_ratio(returns, risk_free), 0.0)


class ForbesMatchTest(unittest.TestCase):
    def test_latest_edition_before_deal(self):
        # deal in Jun 2025 -> Forbes 2024 edition (Oct 2024), 8 months earlier
        self.assertEqual(cross_checks.latest_forbes_before(pd.Period("2025-06", "M")), (2024, 8))

    def test_same_month_edition_not_used(self):
        # the Oct 2025 list may have come out after an Oct 2025 deal, so it is skipped
        self.assertEqual(cross_checks.latest_forbes_before(pd.Period("2025-10", "M")), (2024, 12))

    def test_no_edition_before(self):
        self.assertEqual(cross_checks.latest_forbes_before(pd.Period("2015-01", "M")), (None, None))


class CurrencyTest(unittest.TestCase):
    def test_pence_treated_as_pounds_for_market_values(self):
        self.assertAlmostEqual(multiples_cross_league.to_eur(100, "GBp", {"GBP": 0.5}), 200)

    def test_euro_unchanged(self):
        self.assertEqual(multiples_cross_league.to_eur(100, "EUR", {}), 100)


if __name__ == "__main__":
    unittest.main()
