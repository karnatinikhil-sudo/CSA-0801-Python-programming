"""
CSA-0801: Python Programming - Module 01
Topic: Loops, Iteration Control, Generators, and Algorithmic Patterns

Key Concepts Covered:
1. for loops with range(), enumerate(), and zip()
2. while loops and convergence conditions
3. Loop control statements: break, continue, pass, and loop 'else' clause
4. Prime number generation (Sieve of Eratosthenes)
5. Geometric and ASCII pattern rendering
"""

import math


def generate_primes_sieve(limit: int) -> list[int]:
    """
    Finds all prime numbers up to `limit` using the Sieve of Eratosthenes algorithm.
    Time Complexity: O(n log log n)
    """
    if limit < 2:
        return []

    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False

    for num in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[num]:
            for multiple in range(num * num, limit + 1, num):
                is_prime[multiple] = False

    return [i for i, prime in enumerate(is_prime) if prime]


def find_first_perfect_number_search(search_limit: int = 10000) -> list[int]:
    """
    Finds perfect numbers up to limit using while and for loops with loop-else constructs.
    A perfect number is equal to the sum of its proper positive divisors.
    """
    perfect_numbers = []
    for num in range(2, search_limit + 1):
        divisors_sum = 1
        for d in range(2, int(math.isqrt(num)) + 1):
            if num % d == 0:
                divisors_sum += d
                if d * d != num:
                    divisors_sum += num // d
        if divisors_sum == num:
            perfect_numbers.append(num)
    return perfect_numbers


def render_diamond_pattern(n: int) -> list[str]:
    """
    Renders an ASCII diamond pattern of size n.
    """
    lines = []
    # Upper half + middle
    for i in range(n):
        spaces = " " * (n - i - 1)
        stars = "*" * (2 * i + 1)
        lines.append(f"{spaces}{stars}")
    # Lower half
    for i in range(n - 2, -1, -1):
        spaces = " " * (n - i - 1)
        stars = "*" * (2 * i + 1)
        lines.append(f"{spaces}{stars}")
    return lines


def demonstrate_loop_else(target: int, search_list: list[int]) -> str:
    """
    Demonstrates the Python 'for-else' construct.
    The 'else' block executes ONLY if the loop completes without hitting a 'break'.
    """
    for index, val in enumerate(search_list):
        if val == target:
            return f"Found {target} at index {index} (Hit break, else bypassed)"
    else:
        return f"Target {target} not present in list (Loop completed, else executed)"


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 1.4 - Loops, Iteration & Algorithmic Patterns")
    print("=" * 60)

    print("\n[1] Prime Number Generation (Sieve of Eratosthenes up to 100):")
    primes = generate_primes_sieve(100)
    print(f"  * Found {len(primes)} primes: {primes}")

    print("\n[2] Perfect Numbers Discovery (< 10,000):")
    perfects = find_first_perfect_number_search(10000)
    print(f"  * Perfect Numbers: {perfects}")

    print("\n[3] Python 'for-else' Iteration Flow:")
    dataset = [12, 45, 78, 23, 56, 89, 90]
    print(f"  * Searching 56 in {dataset}: {demonstrate_loop_else(56, dataset)}")
    print(f"  * Searching 99 in {dataset}: {demonstrate_loop_else(99, dataset)}")

    print("\n[4] Geometric Pattern Rendering (Diamond N=5):")
    for row in render_diamond_pattern(5):
        print(f"    {row}")

    print("\n[OK] Lab 1.4 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
