# continued_fraction

Exact continued-fraction arithmetic for rationals and square roots, using only the Python standard library.

## Usage

```python
from fractions import Fraction
from continued_fraction import (
    rational_to_cf,
    cf_to_rational,
    sqrt_to_cf,
    ContinuedFraction,
    QuadraticIrrational,
)

# Rational <-> continued fraction
rational_to_cf(Fraction(355, 113))   # -> [3, 7, 16]
cf_to_rational([3, 7, 16])           # -> Fraction(355, 113)

# sqrt(n) -> (pre_period, period)
sqrt_to_cf(23)                       # -> ([4], [1, 3, 1, 8])

# Object-oriented wrappers
ContinuedFraction.from_rational(Fraction(7, 3)).to_rational()  # -> Fraction(7, 3)
qi = QuadraticIrrational.from_sqrt(2)
list(qi.convergents(5))
# -> [Fraction(1), Fraction(3, 2), Fraction(7, 5), Fraction(17, 12), Fraction(41, 29)]
```

## Why this exists

The library answers two narrow questions exactly: "what is the continued fraction of this rational?" and "what is the periodic continued fraction of sqrt(n)?"  All rational arithmetic uses `fractions.Fraction`, so there is no floating-point round-off anywhere in the rational path.  The square-root algorithm is the standard exact integer iteration on the triple `(m, d, a)` and terminates as soon as a state repeats, which is guaranteed for every non-square positive integer.

The trade-off: this library does not support arbitrary quadratic irrationals of the form `(P + sqrt(D)) / Q` with `P != 0` or `Q != 1`.  It handles `sqrt(n)` and rationals, nothing in between.  Generalizing would require a full quadratic-form solver; that is a larger problem and is deliberately out of scope.

## Edge cases you will hit

- **Negative rationals.** `rational_to_cf(Fraction(-7, 3))` returns `[-3, 1, 2]`, using the floor convention (floor of a negative number rounds toward negative infinity).  This is the standard mathematical definition but differs from truncation.
- **Perfect squares.** `sqrt_to_cf` raises `ValueError` for perfect squares, because their continued fraction is a single integer with no period — a different representation.  Use `rational_to_cf` on the integer root instead.
- **Period minimality.** The period returned by `sqrt_to_cf` is the *minimal* repeating block, found by detecting the first repeated `(m, d)` state.  It is not padded or normalized.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
