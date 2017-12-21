from collections import Counter, Mapping
from itertools import product, accumulate
import random
import numpy as np

from . import Prob

class ProbDist(Mapping):
    """A discrete finite probability distribution."""
    
    __slots__ = [
        '_space',
        '_uniform',
        '_hash',
        '_sorted_outcomes',
        '_sorted_probs',
        '_sorted_sumprobs',
    ]
    
    def __init__(self, *args, **kwargs):
        # Base distribution on Counter (i.e., multiset) data structure
        # See Allen Downey blog post at:
        #   https://allendowney.blogspot.com/2014/05/implementing-pmfs-in-python.html
        self._space = Counter(*args, **kwargs)
        total = sum(self._space.values())
        # Check if all probabilities are equal (uniform distribution)
        # Start off assuming uniform
        self._uniform = True
        last_prob = None
        for event in self._space:
            # Normalize probabilities to sum to 1
            prob = Prob(self._space[event], total)
            self._space[event] = prob
            if last_prob is None:
                # First event so nothing to compare to
                last_prob = prob
            # As soon as we find a different probability value, we know
            # the distribution isn't uniform and we can stop checking
            elif self._uniform:
                self._uniform = (prob == last_prob)
        self._hash = None
        self._sorted_outcomes = None
        self._sorted_probs = None
        self._sorted_sumprobs = None
    
    def prob(self, predicate):
        """Probability of an event."""
        outcomes = self._satisfying(predicate)
        return Prob(
            sum(self._space[x] for x in self._space if x in outcomes)
        )
    
    def subset(self, predicate):
        """Sample space subset satisfying a predicate."""
        return {x for x in self._space if predicate(x)}
 
    def such_that(self, predicate):
        """Distribution of sample space subset satisfying a predicate."""
        outcomes = self._satisfying(predicate)
        return ProbDist(
            {x: self._space[x] for x in self._space if x in outcomes}
        )
    
    def remove(self, events):
        """Renormalized probabilty distribution with certain events removed."""
        return ProbDist(
            {x: self._space[x] for x in self._space if x not in events}
        )
    	 
    def joint(self, other, key_type=None, separator=''):
        """Joint distribution with an independent distribution."""
        result = Counter()
        for (e1, e2) in product(self, other):
            key = ProbDist._key(e1, e2, key_type, separator)
            result[key] += self[e1] * other[e2]
        return ProbDist(result)

    def __add__(self, other):
        """Joint distribution of the sum with an independent distribution."""
        return self.joint(other)
    
    def repeated(self, repeat, key_type=None, separator=''):
        """Joint distribution of repeated independent trials."""
        result = ProbDist(self)
        for _ in range(int(repeat)-1):
            result = result.joint(self, key_type, separator)
        return result
    
    def groupby(self, key=None):
        """Distribution of events grouped by a key."""
        result = Counter()
        for x in self._space:
            result.update({key(x): self[x]})
        return ProbDist(result)
    
    @property
    def pmf(self):
        """Return zipped probability mass function."""
        return zip(*sorted([(x[0], x[1]) for x in self._space.items()]))

    @property
    def is_uniform(self):
        return self._uniform
    
    def choice(self):
        """Draw an outcome with replacement."""
        return self.choices(1)[0]
        
    def choices(self, k):
        """Draw a list of one or more outcomes with replacement."""
        if not self._sorted_outcomes:
            self._setup_sampling()
        weights = self._sorted_sumprobs if self.is_uniform else None
        return random.choices(self._sorted_outcomes, cum_weights=weights, k=k)
    
    def sample(self, k=1):
        """Sample without replacement from distribution."""
        if not self._sorted_outcomes:
            self._setup_sampling()
        if self.is_uniform:
            return random.sample(self._sorted_outcomes, k=k)
        else:
            return list(np.random.choice(
                self._sorted_outcomes,
                p=self._sorted_probs,
                size=k,
                replace=False,
            ))
    
    def most_likely(self, n=1):
        """List of n-most likely outcomes ranked in descending order."""
        if not self._sorted_outcomes:
            self._setup_sampling()
        return self._sorted_outcomes[:n]

    def __getitem__(self, outcome):
        return self._space[outcome]
        
    def __len__(self):
        return len(self._space)
        
    def __contains__(self, event):
        return event in self._space
 
    def __iter__(self):
        return iter(self._space)
        
    def __repr__(self):
        s = ', '.join('{outcome}: {prob}'.format(
            outcome=repr(k), prob=repr(v)
        ) for k, v in sorted(self._space.items()))
        return f'{self.__class__.__name__}' + '({' + s + '})'
    
    def __str__(self):
        s = ', '.join('{outcome}: {prob}'.format(
            outcome=str(k), prob=str(v)
        ) for k, v in sorted(self._space.items()))
        return '{' + s + '}'

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._space.items()))
        return self._hash
    
    # Private helper functions
            
    def _satisfying(self, predicate):
        if callable(predicate):
            return self.subset(predicate)
        else:
            return set(predicate)
    
    def _setup_sampling(self):
        if self.is_uniform:
            self._sorted_outcomes = list(self._space)
        else:
            self._sorted_outcomes = sorted(
                self._space,
                key=self._space.get,
                reverse=True,
            )
            self._sorted_probs = [
                self._space[x] for x in self._sorted_outcomes
            ]
            self._sorted_sumprobs = [
                Prob(x) for x in list(accumulate(self._sorted_probs))
            ]
    
    @staticmethod
    def _key(e1, e2, key_type=None, separator=''):
        try:
            if separator:
                return str(e1) + separator + str(e2)
            elif key_type != tuple:
                return e1 + e2
            elif any([isinstance(x, tuple) for x in [e1, e2]]):
                if isinstance(e1, tuple) and isinstance(e2, tuple):
                    return e1 + e2
                elif isinstance(e1, tuple):
                    return e1 + (e2,)
                else:
                    return (e1,) + e2
            else:
                return (e1, e2)
        except:
            # default to tuple if nothing else works
            return (e1, e2)
