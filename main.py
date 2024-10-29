import timeit
import random
import policies
import math
from output import output

reps = 10
max_cache_size = 128

# Global so they will persist between runs
run_counter = 0
keyset = []


def run(policy: policies.Policy, keyset: list[int]) -> None:
    global run_counter

    policy.lookup(keyset[run_counter % len(keyset)])
    run_counter += 1


def benchmark(
    policy: policies.Policy, shape=-0.75, max_cache_size=128, runs=10000
) -> None:
    global reps
    global keyset
    global run_counter

    # Zipf's law
    if len(keyset) == 0:
        pop = []
        # 1 / (sum of r=1 to N of r^(shape))
        norm_constant = 1 / sum(
            [(i + 1) ** shape for i in range(0, 2 * max_cache_size + 1)]
        )
        for i in range(2 * max_cache_size):
            freq = max_cache_size * norm_constant * ((i + 1) ** shape)
            pop += [i] * math.ceil(freq)

        keyset = random.choices(pop, k=runs)

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

    drrip = policies.DRRIP(max_size=max_cache_size)
    lfu = policies.LFU(max_size=max_cache_size)
    lru = policies.LRU(max_size=max_cache_size)

    # Test different shapes of the input distribution
    shape_data = [["Shape var value", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for shape in range(-100, 5, 5):
        row = [shape / 100]

        row.append(benchmark(lru, shape=shape / 100))
        row.append(benchmark(lfu, shape=shape / 100))
        row.append(benchmark(drrip, shape=shape / 100))

        shape_data.append(row)

        keyset = []

    output("shape", shape_data)
    print("Finished Shape Test")

    keyset = []
    # Test different cache sizes
    cache_data = [["Cache Size", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for size in range(3, 12):
        row = [2**size]

        drrip.max_size = 2**size
        lru.max_size = 2**size
        lfu.max_size = 2**size

        row.append(benchmark(lru, max_cache_size=2**size))
        row.append(benchmark(lfu, max_cache_size=2**size))
        row.append(benchmark(drrip, max_cache_size=2**size))

        cache_data.append(row)

        keyset = []

    drrip.max_size = max_cache_size
    lru.max_size = max_cache_size
    lfu.max_size = max_cache_size

    output("cache_size", cache_data)
    print("Finished cache size Test")

    keyset = []
    # Test different number of lookups
    runs_data = [["Number of Lookups", "LRU Misses", "LFU Misses", "DRRIP Misses"]]
    for runs in range(1000, 11000, 1000):
        row = [runs]

        row.append(benchmark(lru, runs=runs))
        row.append(benchmark(lfu, runs=runs))
        row.append(benchmark(drrip, runs=runs))

        runs_data.append(row)

    output("lookups", runs_data)
    print("Finished Lookups Test")


if __name__ == "__main__":
    test()
