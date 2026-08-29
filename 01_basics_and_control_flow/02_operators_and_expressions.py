"""
CSA-0801: Python Programming - Module 01
Topic: Operators, Expressions, Bitwise Math, and Operator Precedence

Key Concepts Covered:
1. Arithmetic Operators (+, -, *, /, //, %, **)
2. Comparison and Relational Operators
3. Logical Operators (and, or, not) with short-circuit evaluation
4. Bitwise Operators (&, |, ^, ~, <<, >>) & mask operations
5. Membership (in, not in) and Identity (is, is not)
"""


def compute_arithmetic_suite(a: float, b: float) -> dict[str, float]:
    """Computes all standard arithmetic operations on two numbers."""
    if b == 0:
        raise ZeroDivisionError("Denominator cannot be zero for division operations.")
    return {
        "addition": a + b,
        "subtraction": a - b,
        "multiplication": a * b,
        "true_division": a / b,
        "floor_division": a // b,
        "modulus": a % b,
        "exponentiation": a ** (b if abs(b) < 10 else 2),  # safety clamp for demo
    }


def bitwise_manipulations(val1: int, val2: int) -> dict[str, str]:
    """
    Demonstrates bitwise operations and returns their binary representation.
    Useful for low-level systems programming, flags, and hashing.
    """
    return {
        "val1_bin": f"{val1:08b} ({val1})",
        "val2_bin": f"{val2:08b} ({val2})",
        "AND (&)": f"{(val1 & val2):08b} ({val1 & val2})",
        "OR  (|)": f"{(val1 | val2):08b} ({val1 | val2})",
        "XOR (^)": f"{(val1 ^ val2):08b} ({val1 ^ val2})",
        "NOT (~val1)": f"{(~val1):08b} ({~val1})",
        "LSHIFT (val1 << 2)": f"{(val1 << 2):08b} ({val1 << 2})",
        "RSHIFT (val1 >> 2)": f"{(val1 >> 2):08b} ({val1 >> 2})",
    }


def short_circuit_eval_demo() -> list[str]:
    """Demonstrates short-circuit behavior in Boolean logic."""
    logs = []

    def truthy():
        logs.append("Evaluated truthy()")
        return True

    def falsy():
        logs.append("Evaluated falsy()")
        return False

    logs.append("-- Evaluating: falsy() and truthy() --")
    _ = falsy() and truthy()  # truthy() should NOT be called

    logs.append("-- Evaluating: truthy() or falsy() --")
    _ = truthy() or falsy()   # falsy() should NOT be called

    return logs


def calculate_compound_interest(principal: float, rate_pct: float, time_years: float, n_times: int = 12) -> float:
    """
    Calculates compound interest using operator precedence.
    Formula: A = P * (1 + r/n)^(n*t)
    """
    r = rate_pct / 100.0
    amount = principal * ((1 + (r / n_times)) ** (n_times * time_years))
    return round(amount, 2)


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 1.2 - Operators, Expressions & Bitwise Math")
    print("=" * 60)

    print("\n[1] Arithmetic Operations (a=25, b=4):")
    for op, val in compute_arithmetic_suite(25, 4).items():
        print(f"  * {op:<18}: {val}")

    print("\n[2] Bitwise Logic (val1=12 [00001100], val2=25 [00011001]):")
    for name, b_val in bitwise_manipulations(12, 25).items():
        print(f"  * {name:<20}: {b_val}")

    print("\n[3] Short-Circuit Evaluation Flow:")
    for step in short_circuit_eval_demo():
        print(f"  * {step}")

    print("\n[4] Real-world Expression: Compound Interest:")
    p, r, t = 10000.0, 7.5, 3
    final_val = calculate_compound_interest(p, r, t)
    print(f"  * Principal: ${p:,.2f} at {r}% for {t} years -> Total: ${final_val:,.2f}")
    print("\n[OK] Lab 1.2 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
