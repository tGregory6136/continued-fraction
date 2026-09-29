import math
import unittest
from fractions import Fraction

from continued_fraction import (
    ContinuedFraction,
    QuadraticIrrational,
    rational_to_cf,
    cf_to_rational,
    sqrt_to_cf,
)


class TestRationalToCF(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(rational_to_cf(Fraction(5)), [5])

    def test_negative_integer(self):
        self.assertEqual(rational_to_cf(Fraction(-3)), [-3])

    def test_simple_fraction(self):
        # 7/3 = 2 + 1/3 -> [2; 3]
        self.assertEqual(rational_to_cf(Fraction(7, 3)), [2, 3])

    def test_known_value_355_113(self):
        # 355/113 is a famous approximation of pi.
        self.assertEqual(rational_to_cf(Fraction(355, 113)), [3, 7, 16])

    def test_negative_fraction(self):
        # -7/3: floor(-7/3) = -3, remainder 2/3, reciprocal 3/2,
        # floor = 1, remainder 1/2, reciprocal 2 -> [-3, 1, 2]
        self.assertEqual(rational_to_cf(Fraction(-7, 3)), [-3, 1, 2])

    def test_accepts_int(self):
        self.assertEqual(rational_to_cf(4), [4])


class TestCFToRational(unittest.TestCase):
    def test_single_term(self):
        self.assertEqual(cf_to_rational([5]), Fraction(5))

    def test_roundtrip(self):
        for v in [Fraction(0), Fraction(1, 2), Fraction(7, 3), Fraction(355, 113),
                  Fraction(-7, 3), Fraction(99, 100)]:
            self.assertEqual(cf_to_rational(rational_to_cf(v)), v, msg="value=%r" % v)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            cf_to_rational([])

    def test_non_positive_tail_raises(self):
        with self.assertRaises(ValueError):
            cf_to_rational([1, 0])
        with self.assertRaises(ValueError):
            cf_to_rational([1, -2])

    def test_non_int_raises(self):
        with self.assertRaises(TypeError):
            cf_to_rational([1, 2.5])


class TestSqrtToCF(unittest.TestCase):
    def test_sqrt2(self):
        pre, period = sqrt_to_cf(2)
        self.assertEqual(pre, [1])
        self.assertEqual(period, [2])

    def test_sqrt3(self):
        pre, period = sqrt_to_cf(3)
        self.assertEqual(pre, [1])
        self.assertEqual(period, [1, 2])

    def test_sqrt7(self):
        pre, period = sqrt_to_cf(7)
        self.assertEqual(pre, [2])
        self.assertEqual(period, [1, 1, 1, 4])

    def test_sqrt23(self):
        pre, period = sqrt_to_cf(23)
        self.assertEqual(pre, [4])
        self.assertEqual(period, [1, 3, 1, 8])

    def test_perfect_square_raises(self):
        with self.assertRaises(ValueError):
            sqrt_to_cf(9)
        with self.assertRaises(ValueError):
            sqrt_to_cf(1)

    def test_non_positive_raises(self):
        with self.assertRaises(ValueError):
            sqrt_to_cf(0)
        with self.assertRaises(ValueError):
            sqrt_to_cf(-5)


class TestContinuedFractionClass(unittest.TestCase):
    def test_from_rational(self):
        cf = ContinuedFraction.from_rational(Fraction(7, 3))
        self.assertEqual(cf.terms, [2, 3])

    def test_from_rational_int(self):
        cf = ContinuedFraction.from_rational(5)
        self.assertEqual(cf.terms, [5])

    def test_to_rational(self):
        cf = ContinuedFraction([3, 7, 16])
        self.assertEqual(cf.to_rational(), Fraction(355, 113))

    def test_equality(self):
        a = ContinuedFraction([1, 2, 3])
        b = ContinuedFraction([1, 2, 3])
        c = ContinuedFraction([1, 2, 4])
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_invalid_terms_raise(self):
        with self.assertRaises(ValueError):
            ContinuedFraction([1, 0])
        with self.assertRaises(ValueError):
            ContinuedFraction([])

    def test_str(self):
        self.assertEqual(str(ContinuedFraction([1, 2, 3])), "[1; 2; 3]")

    def test_hashable(self):
        s = {ContinuedFraction([1, 2]), ContinuedFraction([1, 2]),
             ContinuedFraction([3])}
        self.assertEqual(len(s), 2)


class TestQuadraticIrrational(unittest.TestCase):
    def test_from_sqrt2(self):
        qi = QuadraticIrrational.from_sqrt(2)
        self.assertEqual(qi.pre, [1])
        self.assertEqual(qi.period, [2])

    def test_convergents_sqrt2(self):
        qi = QuadraticIrrational.from_sqrt(2)
        conv = list(qi.convergents(5))
        # sqrt(2) convergents: 1, 3/2, 7/5, 17/12, 41/29
        self.assertEqual(conv, [
            Fraction(1), Fraction(3, 2), Fraction(7, 5),
            Fraction(17, 12), Fraction(41, 29),
        ])

    def test_convergents_sqrt3(self):
        qi = QuadraticIrrational.from_sqrt(3)
        conv = list(qi.convergents(4))
        # sqrt(3): [1; 1, 2, 1, 2, ...] -> 1, 2, 5/3, 7/4
        self.assertEqual(conv, [
            Fraction(1), Fraction(2), Fraction(5, 3), Fraction(7, 4),
        ])

    def test_str(self):
        qi = QuadraticIrrational([1], [2])
        self.assertEqual(str(qi), "[1; (2)]")

    def test_repr(self):
        qi = QuadraticIrrational([1], [2])
        self.assertEqual(repr(qi), "QuadraticIrrational(pre=[1], period=[2])")

    def test_invalid_period_raises(self):
        with self.assertRaises(ValueError):
            QuadraticIrrational([1], [])
        with self.assertRaises(ValueError):
            QuadraticIrrational([1], [0])

    def test_convergents_count_validation(self):
        qi = QuadraticIrrational.from_sqrt(2)
        with self.assertRaises(ValueError):
            list(qi.convergents(0))

    def test_equality_and_hash(self):
        a = QuadraticIrrational([1], [2])
        b = QuadraticIrrational([1], [2])
        c = QuadraticIrrational([1], [3])
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(hash(a), hash(b))


if __name__ == "__main__":
    unittest.main()
