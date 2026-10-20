"""Shared checks for complete and partial integer-factorization witnesses."""
from collections import Counter
import math

from analyze import is_probable_prime
from battery import gp


def check_product(value, factors, cofactor=1):
    if value < 1 or cofactor < 1 or any(f < 2 for f in factors):
        raise ValueError("Factorization values must be positive; factors must exceed one")
    if math.prod(factors) * cofactor != value:
        raise ValueError(f"Factorization product does not equal {value}")


def check_prime_factors(value, factors, cofactor=1):
    check_product(value, factors, cofactor)
    for factor in factors:
        if not is_probable_prime(factor):
            raise ValueError(f"Composite value in prime-factor list: {factor}")


def pari_factors(value):
    if value < 2:
        raise ValueError("PARI factorization requires an integer exceeding one")
    lines = gp(f"F=factor({value}); for(j=1,#F[,1], "
               'if(!isprime(F[j,1]),error("uncertified factor")); print(F[j,1]," ",F[j,2]));')
    factors = []
    for line in lines:
        fields = line.split()
        if len(fields) != 2:
            raise ValueError(f"Invalid PARI factor record: {line}")
        prime, exponent = map(int, fields)
        if exponent < 1:
            raise ValueError(f"Invalid factor exponent: {line}")
        factors.extend([prime] * exponent)
    check_prime_factors(value, factors)
    return sorted(factors)


def smooth_part(factors, bound=2**40):
    if bound < 2:
        raise ValueError("Smoothness bound must be at least two")
    return math.prod(factor for factor in factors if factor < bound)


def smooth_log2(factors, bound=2**40):
    return math.log2(smooth_part(factors, bound))


def square_divisor_root(factors):
    return math.prod(prime ** (exponent // 2) for prime, exponent in Counter(factors).items())
