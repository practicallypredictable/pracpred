import math

def choose(n, k):
    """Number of ways to choose k items from a list of n items."""
    return math.factorial(n) // (math.factorial(n-k) * math.factorial(k))
