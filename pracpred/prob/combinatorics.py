from math import factorial


def permute(n, k):
    """Number of distinct ordered samples (without replacement) of k items from a set of n items."""
    return factorial(n) // factorial(k)


def choose(n, k):
    """Number of distinct unordered samples (without replacement) of k items from a set of n items."""
    return factorial(n) // (factorial(n - k) * factorial(k))


def multichoose(n, k):
    """Number of distinct ordered samples (with replacement) of k items from a set of n items."""
    return choose(n + k - 1, k)


def strings(n, k):
    """Number of distinct unordered samples (with replacement) of k items from a set of n items."""
    return pow(n, k)
