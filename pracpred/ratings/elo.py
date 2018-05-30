import math
from enum import Enum, auto
from abc import ABC, abstractmethod


class Calculator(ABC):
    """Abstract base class for Elo rating system win probability calculators"""
    def __init__(self, **kwargs):
        super().__init__()

    @abstractmethod
    def win_probs(self, **kwargs):
        """Computed win probabilities for a given match."""
        pass


class LogisticCalculator(Calculator):
    """Logistic win probability calculator for Elo rating system"""
    def __init__(self, *, odds_scale=10, rating_scale=400):
        self.odds_scale = odds_scale
        self.rating_scale = rating_scale
        super().__init__()

    def win_probs(self, *, elo1, elo2, adjustment):
        odds_factor1 = math.pow(self.odds_scale, elo1/self.rating_scale)
        odds_factor2 = math.pow(self.odds_scale, elo2/self.rating_scale)
        adj = math.pow(self.odds_scale, adjustment/self.rating_scale)
        denom = odds_factor2 + adj*odds_factor1
        expected1 = (adj*odds_factor1) / denom
        expected2 = odds_factor2 / denom
        return expected1, expected2


class Multiplier(ABC):
    """Abstract base class for Elo rating system multipliers"""
    def __init__(self, **kwargs):
        super().__init__()

    @abstractmethod
    def value(self, **kwargs):
        """Value of multiplier"""
        pass


class ConstantMultiplier(Multiplier):
    """Constant Elo rating system multiplier"""
    def __init__(self, *, constant):
        self.constant = constant

    def value(self, **kwargs):
        return self.constant


class MatchOutcome(Enum):
    DRAW = auto()
    WIN1 = auto()
    WIN2 = auto()


class Updater():
    def __init__(self, *, calculator, multiplier):
        self.calculator = calculator
        self.multiplier = multiplier

    def update(self, *, outcome, elo1, elo2, adjustment, **kwargs):
        prob1, prob2 = self.calculator.win_probs(
            elo1=elo1,
            elo2=elo2,
            adjustment=adjustment
        )
        if outcome == MatchOutcome.DRAW:
            score1 = 0.5
            score2 = 0.5
        elif outcome == MatchOutcome.WIN1:
            score1 = 1.0
            score2 = 0.0
        elif outcome == MatchOutcome.WIN2:
            score1 = 0.0
            score2 = 1.0
        else:
            raise ValueError('invalid outcome', outcome)
        k = self.multiplier.value(
            outcome=outcome,
            elo1=elo1,
            elo2=elo2,
            adjustment=adjustment,
            **kwargs
        )
        new_elo1 = elo1 + k*(score1 - prob1)
        new_elo2 = elo2 + k*(score2 - prob2)
        return new_elo1, new_elo2
