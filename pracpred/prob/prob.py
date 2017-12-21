import math
from fractions import Fraction

class Prob(Fraction):
    """Representation of a probability."""

    # There are no attributes for a probability other than the fraction value
    __slots__ = []

    def __new__(cls, numerator=0, denominator=None):
        """Create a new probability with a value between 0 and 1 inclusive."""
        p, n, d = Prob._format(numerator, denominator)
        if p < 0:
            raise ValueError('Prob cannot be negative')
        if p > 1:
            raise ValueError('Prob cannot be greater than one')
        return super().__new__(cls, p)

    @property
    def fractional_odds_against(self):
        """Express the probability as fractional odds against."""
        return Fraction(1/self - 1) if self > 0 else math.inf
    
    @property
    def fractional_odds_on(self):
        """Express the probability as fractional odds on."""
        return 1/self.fractional_odds_against
    
    @property
    def decimal_odds_against(self):
        """Express the probabilty as decimal odds against."""
        return Fraction(1/self) if self > 0 else math.inf
    
    @property
    def decimal_odds_on(self):
        """Express the probability as decimal odds on."""
        return 1/self.decimal_odds_against
    
    @property
    def moneyline_odds_against(self):
        """Express the probability as moneyline odds against."""
        if self == 1:
            return -math.inf
        elif self > Fraction(1,2):
            return -100 * self / (1-self)
        elif self > 0:
            return 100 * (1-self) / self
        else:
            return math.inf

    @property
    def moneyline_odds_on(self):
        """Express the probability as moneyline odds on."""
        return 1/self.moneyline_odds_against
    
    @classmethod
    def from_fractional_odds_against(cls, numerator=0, denominator=None):
        """Create a probability from fractional odds against."""
        n, d = cls._format_fractional(numerator, denominator)
        return cls(d, n+d)
    
    @classmethod
    def from_fractional_odds_on(cls, numerator=0, denominator=None):
        """Create a probability from fractional odds on."""
        n, d = cls._format_fractional(numerator, denominator)
        return cls(n, n+d)
        
    @classmethod
    def from_decimal_odds_against(cls, numerator=0, denominator=None):
        """Create a probability from decimal odds against."""
        n, d = cls._format_decimal(numerator, denominator)
        return cls(d, n)

    @classmethod
    def from_decimal_odds_on(cls, numerator=0, denominator=None):
        """Create a probability from decimal odds on."""
        n, d = cls._format_decimal(numerator, denominator)
        return cls(n, d)

    @classmethod
    def from_moneyline_odds_against(cls, numerator=0, denominator=None):
        """Create a probability from moneyline odds against."""
        n, d = cls._format_moneyline(numerator, denominator)
        return cls(d, n+d)

    @classmethod
    def from_moneyline_odds_on(cls, numerator=0, denominator=None):
        """Create a probability from moneyline odds against."""
        n, d = cls._format_moneyline(numerator, denominator)
        return cls(n, n+d)

    @staticmethod
    def _ratio_from_float(f):
        if int(f) == f:
            return (int(f), 1)
        s = str(f)
        s = s.split('.')
        n = int(''.join(s))
        d = 10 ** len(s[1])
        return (n, d)

    @staticmethod
    def _format(numerator, denominator):
        if isinstance(numerator, str) and not denominator:
            numerator = numerator.replace(':', '/')
        if isinstance(numerator, float) and not denominator:
            numerator, denominator = Prob._ratio_from_float(numerator)
        result = Fraction(numerator, denominator)
        return (result, result.numerator, result.denominator)

    @staticmethod
    def _format_fractional(n, d):
        odds, n, d = Prob._format(n, d)
        if odds < 0:
            raise ValueError('Fractional odds cannot be negative')
        return (n, d)

    @staticmethod
    def _format_decimal(n, d):
        odds, n, d = Prob._format(n, d)
        if odds <= 0:
            raise ValueError('Decimal odds must be positive')
        return (n, d)
        
    @staticmethod
    def _format_moneyline(n, d):
        odds, n, d = Prob._format(n, d)
        if odds > 0:
            odds = Fraction(odds/100)
        elif odds < 0:
            odds = Fraction(-100/odds)
        else:
            raise ValueError('Moneyline odds cannot be zero')
        n = odds.numerator
        d = odds.denominator
        return (n, d)
