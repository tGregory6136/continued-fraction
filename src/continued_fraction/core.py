"""Exact continued-fraction arithmetic for rationals and quadratic irrationals.

Design decisions (documented once, here):

* Continued fractions are stored as Python lists of ints.  The first element
  is the integer part (may be negative, zero, or positive); every subsequent
  element is a positive integer.  This is the canonical simple continued
  fraction form.

* Finite lists represent rationals.  Infinite lists cannot be stored, so
  *periodic* continued fractions (which represent quadratic irrationals) are
  captured by the QuadraticIrrational class, which holds the pre-period and
  the repeating period explicitly.

* We use the Fraction type from the standard library for all rational
  intermediate work so there is no floating-point round-off anywhere in the
  rational path.

* The square-root expansion follows the classic algorithm: maintain a pair
  (m, d) and the floor a, iterating until (m, d) returns to a previously seen
  state, which marks the start of the period.  This is exact integer
  arithmetic and terminates for every non-square positive integer.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import List, Tuple


__all__ = [
    "ContinuedFraction",
    "QuadraticIrrational",
    "rational_to_cf",
    "cf_to_rational",
    "sqrt_to_cf",
]


def rational_to_cf(x: Fraction) -> List[int]:
    """Return the simple continued fraction of the rational ``x``.

    The result is a list ``[a0, a1, ...]`` where ``a0`` may be any integer and
    every later term is strictly positive.  For integers the result is the
    one-element list ``[a0]``.

    The Euclidean algorithm is used directly; this is exact and terminates
    because the numerator strictly decreases in absolute value at each step
    once the integer part is removed.
    """
    if not isinstance(x, Fraction):
        x = Fraction(x)
    terms: List[int] = []
    while True:
        a = math.floor(x)
        terms.append(a)
        frac = x - a
        if frac == 0:
            return terms
        x = Fraction(1) / frac


def cf_to_rational(terms: List[int]) -> Fraction:
    """Convert a finite simple continued fraction back to a :class:`Fraction`.

    ``terms`` must be a non-empty list of ints with the first element allowed
    to be any integer and every subsequent element strictly positive.
    """
    if not terms:
        raise ValueError("cf_to_rational requires a non-empty list of terms")
    if not all(isinstance(t, int) for t in terms):
        raise TypeError("all continued-fraction terms must be ints")
    for i, t in enumerate(terms):
        if i == 0:
            continue
        if t <= 0:
            raise ValueError(
                "every term after the first must be positive; got %r at index %d" % (t, i)
            )
    # Evaluate from the tail using Fraction for exactness.
    acc: Fraction = Fraction(terms[-1])
    for t in reversed(terms[:-1]):
        acc = Fraction(t) + Fraction(1) / acc
    return acc


def sqrt_to_cf(n: int) -> Tuple[List[int], List[int]]:
    """Return ``(pre_period, period)`` for the continued fraction of ``sqrt(n)``.

    ``n`` must be a positive non-square integer.  The pre-period is always a
    single element ``[a0]`` for ``sqrt(n)``; we return it as a list for a
    uniform interface.  The period is the minimal repeating block.

    Algorithm (standard, exact): maintain the triple ``(m, d, a)`` where

        m_{k+1} = d_k * a_k - m_k
        d_{k+1} = (n - m_{k+1}^2) // d_k
        a_{k+1} = floor((a0 + m_{k+1}) / d_{k+1})

    The state ``(m, d)`` determines the future, so the period begins when a
    state repeats.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if n <= 0:
        raise ValueError("n must be a positive integer")
    root = math.isqrt(n)
    if root * root == n:
        raise ValueError("n must not be a perfect square")
    a0 = root
    pre = [a0]
    period: List[int] = []
    m, d, a = 0, 1, a0
    seen: dict = {}
    while True:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        key = (m, d)
        if key in seen:
            start = seen[key]
            period = period[start:]
            break
        seen[key] = len(period)
        period.append(a)
    return pre, period


class ContinuedFraction:
    """A finite (rational) continued fraction.

    Stores the term list and supports conversion to/from :class:`Fraction`,
    equality, and a string representation in bracket notation.
    """

    __slots__ = ("_terms",)

    def __init__(self, terms: List[int]) -> None:
        if not isinstance(terms, list):
            raise TypeError("terms must be a list of ints")
        if not terms:
            raise ValueError("terms must be non-empty")
        if not all(isinstance(t, int) for t in terms):
            raise TypeError("all terms must be ints")
        for i, t in enumerate(terms):
            if i == 0:
                continue
            if t <= 0:
                raise ValueError("term %d must be positive, got %r" % (i, t))
        self._terms = list(terms)

    @classmethod
    def from_rational(cls, x) -> "ContinuedFraction":
        """Build from an int, :class:`Fraction`, or anything Fraction accepts."""
        return cls(rational_to_cf(Fraction(x)))

    @classmethod
    def from_terms(cls, terms: List[int]) -> "ContinuedFraction":
        return cls(terms)

    @property
    def terms(self) -> List[int]:
        return list(self._terms)

    def to_rational(self) -> Fraction:
        return cf_to_rational(self._terms)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContinuedFraction):
            return self._terms == other._terms
        return NotImplemented

    def __hash__(self) -> int:
        return hash(tuple(self._terms))

    def __repr__(self) -> str:
        return "ContinuedFraction(%r)" % (self._terms,)

    def __str__(self) -> str:
        return "[%s]" % "; ".join(str(t) for t in self._terms)


class QuadraticIrrational:
    """A quadratic irrational represented by a periodic continued fraction.

    Specifically, this models numbers of the form ``(P + sqrt(D)) / Q`` where
    the continued fraction is eventually periodic.  We store the pre-period
    and the minimal repeating period as lists of ints.

    The primary constructor takes ``pre`` and ``period`` directly.  Use
    :meth:`from_sqrt` to build the representation for ``sqrt(n)``.
    """

    __slots__ = ("_pre", "_period")

    def __init__(self, pre: List[int], period: List[int]) -> None:
        if not isinstance(pre, list) or not isinstance(period, list):
            raise TypeError("pre and period must be lists of ints")
        if not pre:
            raise ValueError("pre must be non-empty")
        if not period:
            raise ValueError("period must be non-empty")
        if not all(isinstance(t, int) for t in pre):
            raise TypeError("pre must contain only ints")
        if not all(isinstance(t, int) for t in period):
            raise TypeError("period must contain only ints")
        for i, t in enumerate(pre):
            if i == 0:
                continue
            if t <= 0:
                raise ValueError("pre term %d must be positive" % i)
        for t in period:
            if t <= 0:
                raise ValueError("all period terms must be positive")
        self._pre = list(pre)
        self._period = list(period)

    @classmethod
    def from_sqrt(cls, n: int) -> "QuadraticIrrational":
        pre, period = sqrt_to_cf(n)
        return cls(pre, period)

    @property
    def pre(self) -> List[int]:
        return list(self._pre)

    @property
    def period(self) -> List[int]:
        return list(self._period)

    def convergents(self, count: int):
        """Yield the first ``count`` rational convergents as :class:`Fraction`.

        The convergents are the best rational approximations to the irrational
        and are computed by unrolling the (infinite) continued fraction up to
        ``count`` terms total.
        """
        if not isinstance(count, int) or count < 1:
            raise ValueError("count must be a positive int")
        seq: List[int] = []
        for i in range(count):
            if i < len(self._pre):
                seq.append(self._pre[i])
            else:
                idx = (i - len(self._pre)) % len(self._period)
                seq.append(self._period[idx])
            yield cf_to_rational(seq)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, QuadraticIrrational):
            return self._pre == other._pre and self._period == other._period
        return NotImplemented

    def __hash__(self) -> int:
        return hash((tuple(self._pre), tuple(self._period)))

    def __repr__(self) -> str:
        return "QuadraticIrrational(pre=%r, period=%r)" % (self._pre, self._period)

    def __str__(self) -> str:
        pre_str = "; ".join(str(t) for t in self._pre)
        per_str = ", ".join(str(t) for t in self._period)
        return "[%s; (%s)]" % (pre_str, per_str)
