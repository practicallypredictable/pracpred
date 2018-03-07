from collections import Counter, Mapping
import itertools as it
import random
import numpy as np

from pracpred.prob import Prob


class ProbDist(Mapping):
    """A discrete finite probability distribution."""

    __slots__ = [
        '_name',
        '_space',
        '_uniform',
        '_hash',
        '_sorted_elements',
        '_sorted_probs',
        '_sorted_cumprobs',
    ]

    def __init__(self, *args, **kwargs):
        # Base distribution on Counter (i.e., multiset) data structure
        # See Allen Downey blog post at:
        #   https://allendowney.blogspot.com/2014/05/implementing-pmfs-in-python.html
        self._name = None
        self._space = Counter(*args, **kwargs)
        total = sum(self._space.values())
        self._uniform = True
        prior_value = None
        for element in self._space:
            p = Prob(self._space[element], total)
            self._space[element] = p
            if prior_value is None:
                prior_value = p
            elif self._uniform:
                self._uniform = (p == prior_value)
        self._hash = None
        self._sorted_elements = None
        self._sorted_probs = None
        self._sorted_cumprobs = None

    def prob(self, event):
        """Probability of an event."""
        if callable(event):
            event = self.subset_such_that(event)
        return Prob(sum(self._space[x] for x in self._space if x in event))

    def such_that(self, condition_true_for):
        """Distribution of sample space subset satisfying a condition."""
        return self.__class__({x: self._space[x] for x in self._space if condition_true_for(x)})

    def subset_such_that(self, condition_true_for):
        """Sample space subset satisfying a condition."""
        return {x for x in self._space if condition_true_for(x)}

    def exclude(self, event):
        """Renormalized probability distribution after removing an event."""
        return self.__class__({x: self._space[x] for x in self._space if x not in self.subset_such_that(event)})

    def joint(self, other, product=False, separator=''):
        """Joint distribution with an independent distribution."""
        if not isinstance(other, ProbDist):
            return NotImplemented
        result = Counter()
        for (e1, e2) in it.product(self, other):
            key = ProbDist._key(e1, e2, product, separator)
            result[key] += self[e1] * other[e2]
        return self.__class__(result)

    def __add__(self, other):
        """Joint distribution of the sum with an independent distribution."""
        return self.joint(other)

    def repeated(self, repeat, product=False, separator=''):
        """Joint distribution of repeated independent trials."""
        result = self.__class__(self)
        for _ in range(int(repeat) - 1):
            result = result.joint(self, product, separator)
        return result

    def groupby(self, key=None):
        """Distribution of events grouped by a key."""
        result = Counter()
        for x in self._space:
            result.update({key(x): self[x]})
        return self.__class__(result)

    def most_common(self, k=1):
        """Most common elements."""
        return self._space.most_common(k)

    @property
    def zipped(self):
        """Return zipped probability mass function."""
        return zip(*sorted([(x[0], x[1]) for x in self._space.items()]))

    @property
    def is_uniform(self):
        return self._uniform

    @staticmethod
    def random_seed(seed=1):
        random.seed(seed)
        np.random.seed(seed)

    def choice(self):
        """Draw an outcome with replacement."""
        return self.choices(1)[0]

    def choices(self, k):
        """Draw one or more outcomes with replacement."""
        if not self._sorted_elements:
            self._setup_sampling()
        weights = self._sorted_cumprobs if not self.is_uniform else None
        return random.choices(self._sorted_elements, cum_weights=weights, k=k)

    def sample(self, k=1):
        """Sample without replacement."""
        if not self._sorted_elements:
            self._setup_sampling()
        if self.is_uniform:
            return random.sample(self._sorted_elements, k=k)
        else:
            return list(np.random.choice(
                self._sorted_elements,
                p=self._sorted_probs,
                size=k,
                replace=False,
            ))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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
        if self._name:
            return str(self._name) + ' = {' + s + '}'
        else:
            return '{' + s + '}'

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._space.items()))
        return self._hash

    def copy(self):
        return self.__class__(self._space.copy())

    # Private helper functions

    def _setup_sampling(self):
        # sort descending by probability
        # do this even for uniform distributions even thought sorting doesn't matter
        self._sorted_elements = sorted(self._space, key=self._space.get, reverse=True)
        self._sorted_probs = [self._space[x] for x in self._sorted_elements]
        self._sorted_cumprobs = [Prob(x) for x in list(it.accumulate(self._sorted_probs))]

    @staticmethod
    def _key(e1, e2, product=False, separator=''):
        try:
            if separator:
                return str(e1) + separator + str(e2)
            elif not product:
                return e1 + e2
            elif any([isinstance(x, tuple) for x in [e1, e2]]):
                if isinstance(e1, tuple) and isinstance(e2, tuple):
                    return e1 + e2
                elif isinstance(e1, tuple):
                    return e1 + (e2,)
                else:
                    return (e1,) + e2
            else:
                return e1, e2
        except TypeError:
            # default to tuple if nothing else works
            return e1, e2
