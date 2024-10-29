import timeit
import random
import policies
import math
from output import output

reps = 100
max_cache_size = 128
g_runs = 10000

# Global so they will persist between runs
run_counter = 0
keyset = []


def zipf(num_unique: int, shape: float, request_count: int) -> list[int]:
    """
    Generate a sequence of requests following a Zipfian distribution.

    Parameters:
    - num_unique: Total number of unique items (keys).
    - shape: Zipf exponent (β) controlling the skew.
    - request_count: Total number of requests to generate.

    Returns:
    - A list of requests (item accesses) following the Zipfian distribution.
    """
    ranks = range(1, num_unique + 1)
    probs = [r**shape for r in ranks]
    total_probs = sum(probs)
    norm_probs = [p / total_probs for p in probs]

    return random.choices(
        population=ranks,
        weights=norm_probs,
        k=request_count,
    )


def run(policy: policies.Policy, keyset: list[int]) -> None:
    global run_counter

    policy.lookup(keyset[run_counter % len(keyset)])
    run_counter += 1


def benchmark(
    policy: policies.Policy, shape=-0.75, max_cache_size=128, runs=g_runs
) -> None:
    global reps
    global keyset
    global run_counter

    # Zipf's law
    keyset = zipf(2 * max_cache_size, shape, runs)

    timeit.repeat(
        "run(policy, keyset)",
        globals=globals() | locals(),
        repeat=reps,
        number=runs,
        setup="policy.new_run()\nrun_counter = 0",
    )

    misses = policy.get_misses()

    policy.misses = []
    run_counter = 0

    return misses


def test():
    global keyset
    global max_cache_size
    global g_runs

    drrip = policies.DRRIP(max_size=max_cache_size)
    lfu = policies.LFU(max_size=max_cache_size)
    lru = policies.LRU(max_size=max_cache_size)

    # Test different shapes of the input distribution
    shape_data = [["Shape var value", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for shape in range(-100, 5, 25):
        row = [shape / 100]

        row.append(benchmark(lru, shape=shape / 100) / g_runs)
        row.append(benchmark(lfu, shape=shape / 100) / g_runs)
        row.append(benchmark(drrip, shape=shape / 100) / g_runs)

        shape_data.append(row)


    output("shape", shape_data)
    print("Finished Shape Test")

    # Test different cache sizes
    cache_data = [["Cache Size", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for size in range(3, 14):
        row = [2**size]

        drrip.max_size = 2**size
        lru.max_size = 2**size
        lfu.max_size = 2**size

        row.append(benchmark(lru, max_cache_size=2**size) / g_runs)
        row.append(benchmark(lfu, max_cache_size=2**size) / g_runs)
        row.append(benchmark(drrip, max_cache_size=2**size) / g_runs)

        cache_data.append(row)


    drrip.max_size = max_cache_size
    lru.max_size = max_cache_size
    lfu.max_size = max_cache_size

    output("cache_size", cache_data)
    print("Finished cache size Test")

    # Test different number of lookups
    runs_data = [["Number of Lookups", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for runs in range(1000, 11000, 1000):
        row = [runs]

        row.append(benchmark(lru, runs=runs) / runs)
        row.append(benchmark(lfu, runs=runs) / runs)
        row.append(benchmark(drrip, runs=runs) / runs)

        runs_data.append(row)

    output("lookups", runs_data)
    print("Finished Lookups Test")


if __name__ == "__main__":
    test()
