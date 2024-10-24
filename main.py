import timeit
import random
import policies
import math

runs = 1000
reps = 10
max_cache_size = 128
# should be < 0
# controls decay of the amount of items in the keyset
# -1 supposedly makes it equals to kipf's law
shape = -1


def benchmark(policy: policies.Policy) -> None:
    global runs
    global reps
    global max_cache_size

    # Zipf's law, I guess
    # (This is cool math stuff)
    keyset = []
    for i in range(1, 2 * max_cache_size):
        freq = max_cache_size * (i**-0.5)
        keyset += [i] * math.ceil(freq)

    # exit(0)
    times = timeit.repeat(
        "policy.lookup(random.choice(keyset), 'inputs/small.json')",
        globals=globals() | locals(),
        repeat=reps,
        number=runs,
    )

    print(
        f"\n{policy.misses} misses using {policy} | {policy.misses / (runs * reps) * 100}% missed"
    )
    print(f"{sum(times) * 1000}ms taken total")
    print(f"Minimum time taken: {min(times) * 1000}ms")


lfu = policies.LFU(max_cache_size)
benchmark(lfu)

lru = policies.LRU(max_cache_size)
benchmark(lru)
