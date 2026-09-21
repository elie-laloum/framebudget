import unittest
from framebudget.core import sample_offsets, pareto, BudgetError


class CoreTests(unittest.TestCase):
    def test_samples_cover_endpoints_and_short_clips(self):
        self.assertEqual(sample_offsets(10, 3, 2), ([0.0, 4.0, 8.0], 2))
        self.assertEqual(sample_offsets(1, 3, 2), ([0.0], 1))
        with self.assertRaises(BudgetError):
            sample_offsets(10, 0, 2)

    def test_frontier_preserves_real_tradeoffs(self):
        small = dict(sample_bytes=10, encode_seconds=3, quality=90)
        fast = dict(sample_bytes=15, encode_seconds=1, quality=95)
        worse = dict(sample_bytes=20, encode_seconds=4, quality=80)
        self.assertEqual(pareto([small, fast, worse]), [small, fast])


if __name__ == '__main__':
    unittest.main()
