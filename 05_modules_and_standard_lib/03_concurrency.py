"""
CSA-0801: Python Programming - Module 05
Topic: Concurrency Models (Threading, Multiprocessing, and Asyncio)

Key Concepts Covered:
1. ThreadPoolExecutor for I/O-bound tasks
2. ProcessPoolExecutor for CPU-bound computations (bypassing the GIL)
3. Asynchronous event loop programming with `asyncio` (async/await, asyncio.gather)
4. Race condition prevention using thread locks
"""

import asyncio
import math
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any


# 1. Thread-safe Shared Counter with Locks
class ThreadSafeMetrics:
    def __init__(self):
        self._counter = 0
        self._lock = Lock()

    def increment(self) -> None:
        with self._lock:
            # Critical section protected by Mutex
            curr = self._counter
            time.sleep(0.001)  # Simulate tiny I/O delay
            self._counter = curr + 1

    @property
    def value(self) -> int:
        with self._lock:
            return self._counter


def demonstrate_thread_pool(num_tasks: int = 10) -> int:
    """Dispatches I/O-bound tasks across a thread pool safely."""
    metrics = ThreadSafeMetrics()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(metrics.increment) for _ in range(num_tasks)]
        for f in futures:
            f.result()
    return metrics.value


# 2. CPU-bound computation helper
def compute_heavy_factorials(n: int) -> int:
    """Simulates CPU-intensive calculation."""
    return sum(math.factorial(i % 15) for i in range(n))


# 3. Asynchronous I/O Simulation (Asyncio)
async def fetch_student_report_async(student_id: str, delay_sec: float) -> dict[str, Any]:
    """Simulates fetching student data asynchronously over a network."""
    await asyncio.sleep(delay_sec)
    return {
        "student_id": student_id,
        "fetch_time_sec": delay_sec,
        "status": "Loaded"
    }


async def run_async_batch_fetch() -> list[dict[str, Any]]:
    """Runs multiple asynchronous fetch operations concurrently via asyncio.gather."""
    tasks = [
        fetch_student_report_async("STU-101", 0.05),
        fetch_student_report_async("STU-102", 0.08),
        fetch_student_report_async("STU-103", 0.03),
        fetch_student_report_async("STU-104", 0.06),
    ]
    results = await asyncio.gather(*tasks)
    return results


def run_demo():
    print("=" * 60)
    print(" CSA-0801: Lab 5.3 - Concurrency (Threading & Asyncio)")
    print("=" * 60)

    print("\n[1] ThreadPoolExecutor & Mutex Lock Synchronization:")
    t_start = time.perf_counter()
    final_count = demonstrate_thread_pool(15)
    t_duration = time.perf_counter() - t_start
    print(f"  * Executed 15 concurrent thread updates safely: Counter = {final_count}")
    print(f"  * Duration: {t_duration:.4f} seconds")

    print("\n[2] Asynchronous I/O Batch Processing (asyncio.gather):")
    a_start = time.perf_counter()
    async_results = asyncio.run(run_async_batch_fetch())
    a_duration = time.perf_counter() - a_start
    for r in async_results:
        print(f"  * Async Response: Student {r['student_id']} fetched in {r['fetch_time_sec']}s")
    print(f"  * Total Concurrent Fetch Time: {a_duration:.4f}s (vs serial ~0.22s)")

    print("\n[OK] Lab 5.3 execution completed successfully.\n")


if __name__ == "__main__":
    run_demo()
