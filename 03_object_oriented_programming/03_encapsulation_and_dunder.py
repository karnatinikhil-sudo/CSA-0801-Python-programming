"""
CSA-0801: Python Programming - Module 03
Topic: Encapsulation, Properties, Operator Overloading, and Dunder Methods

Key Concepts Covered:
1. Private attributes (__attr), Name Mangling, and Protected attributes (_attr)
2. The @property decorator (Getter, Setter, Deleter, and Data Validation)
3. Operator Overloading: __add__, __sub__, __mul__, __eq__, __lt__
4. Collection protocol dunder methods: __len__, __getitem__, __iter__, __contains__
"""

from typing import Iterator


class GradeVector:
    """Demonstrates Operator Overloading for academic grade vectors."""

    def __init__(self, scores: list[float]):
        self._scores = [float(s) for s in scores]

    def __len__(self) -> int:
        return len(self._scores)

    def __getitem__(self, index: int) -> float:
        return self._scores[index]

    def __iter__(self) -> Iterator[float]:
        return iter(self._scores)

    def __contains__(self, item: float) -> bool:
        return item in self._scores

    def __add__(self, other: "GradeVector") -> "GradeVector":
        """Vector addition: v1 + v2."""
        if len(self) != len(other):
            raise ValueError("GradeVectors must have identical dimensions to add.")
        return GradeVector([a + b for a, b in zip(self._scores, other._scores)])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GradeVector):
            return False
        return self._scores == other._scores

    def __lt__(self, other: "GradeVector") -> bool:
        """Compares two vectors based on their average score."""
        return self.average() < other.average()

    def average(self) -> float:
        return sum(self._scores) / len(self._scores) if self._scores else 0.0

    def __repr__(self) -> str:
        return f"GradeVector({self._scores})"


class BankAccount:
    """Demonstrates Encapsulation, Name Mangling, and Property Decorators."""

    def __init__(self, account_holder: str, initial_balance: float = 0.0):
        self.account_holder = account_holder
        self.__balance = 0.0  # Private attribute (name mangled to _BankAccount__balance)
        self.balance = initial_balance  # Uses the property setter

    @property
    def balance(self) -> float:
        """Getter for balance."""
        return self.__balance

    @balance.setter
    def balance(self, amount: float) -> None:
        """Setter with validation invariant."""
        if amount < 0:
            raise ValueError("Account balance cannot be negative.")
        self.__balance = amount

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.__balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.__balance -= amount


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 3.3 - Encapsulation, Properties & Dunder Methods")
    print("=" * 60)

    print("\n[1] Encapsulation & Property Validation:")
    acct = BankAccount("Nikhil Karnati", 1500.0)
    print(f"  * Created Account: {acct.account_holder} -> Balance: ${acct.balance:,.2f}")
    acct.deposit(500.0)
    print(f"  * Deposited $500  -> Balance: ${acct.balance:,.2f}")
    acct.withdraw(200.0)
    print(f"  * Withdrew $200   -> Balance: ${acct.balance:,.2f}")

    # Demonstrate name mangling
    print(f"  * Name Mangled Access: acct._BankAccount__balance = ${getattr(acct, '_BankAccount__balance'):,.2f}")

    print("\n[2] Operator Overloading with GradeVector:")
    v1 = GradeVector([80.0, 85.0, 90.0])
    v2 = GradeVector([5.0, 5.0, 5.0])
    v_total = v1 + v2
    print(f"  * v1: {v1} (Avg: {v1.average():.1f})")
    print(f"  * v2: {v2}")
    print(f"  * v1 + v2: {v_total} (Avg: {v_total.average():.1f})")
    print(f"  * v1 < v_total comparison: {v1 < v_total}")
    print(f"  * Length of vector: {len(v_total)}")
    print(f"  * 90.0 in v_total? {90.0 in v_total}")

    print("\n[OK] Lab 3.3 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
