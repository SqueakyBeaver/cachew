import timeit
import random
import policies
import math

runs = 1000
reps = 100
max_cache_size = 64

# should be < 0
# controls decay of the amount of items in the keyset
# -1 supposedly makes it equals to kipf's law
shape = -0.75

def run(policy: policies.Policy, keyset: list[int]) -> None:
    policy.lookup(random.choice(keyset), 'inputs/small.json')


def benchmark(policy: policies.Policy) -> None:
    global runs
    global reps
    global max_cache_size
    global shape

    # Zipf's law, I guess
    # (This is cool math stuff)
    keyset = []
    for i in range(1, 2 * max_cache_size):
        freq = max_cache_size * (i**shape)
        keyset += [i] * math.ceil(freq)

    times = timeit.repeat(
        "run(policy, keyset)",
        globals=globals() | locals(),
        repeat=reps,
        number=runs,
        setup="policy.new_run()"
    )

    misses = policy.get_misses()

    print(
        f"\n{misses} misses using {policy} ({misses - max_cache_size} after filled) | {misses / (runs * reps) * 100}% missed"
    )
    print(f"{sum(times) * 1000}ms taken total")
    print(f"Minimum time taken: {min(times) * 1000}ms")


drrip = policies.DRRIP(max_size=max_cache_size)
benchmark(drrip)

lfu = policies.LFU(max_cache_size)
benchmark(lfu)

lru = policies.LRU(max_cache_size)
benchmark(lru)
