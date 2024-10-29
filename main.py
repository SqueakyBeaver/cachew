import statistics
import random
import policies
import math
from output import output

# Odd number means a nice, round median
g_reps = 1
g_requests = 100000
g_cache_size = 128 / g_requests

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
    ranks = range(num_unique)
    probs = [(r + 1) ** shape for r in ranks]
    total_probs = sum(probs)
    norm_probs = [p / total_probs for p in probs]

    return random.choices(
        population=ranks,
        weights=norm_probs,
        k=request_count,
    )

def run_lookup(policy: policies.Policy) -> None:
    global run_counter
    global keyset

    policy.lookup(keyset[run_counter % len(keyset)])
    run_counter += 1


def benchmark(
    policies: list[policies.Policy],
    shape=-0.75,
    cache_size=g_cache_size,
    requests=g_requests,
) -> dict[str, policies.Policy]:
    global g_reps
    global keyset

    cache_size = math.floor(cache_size * requests)

    total_hits = {
        "LRU": [],
        "LFU": [],
        "DRRIP": [],
    }
    for _ in range(g_reps):
        # Make a new keyset for each rep
        keyset = zipf(cache_size * 2, shape, requests)

        for policy in policies:
            name = str(policy)
            policy.max_size = cache_size
            policy.new_run()

            for x in range(requests):
                policy.lookup(keyset[x % len(keyset)])

            total_hits[name].append(policy.get_hits())

    for p in policies:
        p.hits = []

    return {
        "LRU": statistics.median(total_hits["LRU"]),
        "LFU": statistics.median(total_hits["LFU"]),
        "DRRIP": statistics.median(total_hits["DRRIP"]),
    }


def test():
    global keyset
    global g_cache_size
    global g_requests

    drrip = policies.DRRIP(max_size=math.floor(g_cache_size * g_requests))
    lfu = policies.LFU(max_size=math.floor(g_cache_size * g_requests))
    lru = policies.LRU(max_size=math.floor(g_cache_size * g_requests))

    control_data = [["LRU Hits", "LFU Hits", "DRRIP Hits"]]

    hits = benchmark([drrip, lfu, lru])

    control_data += [
        [
            hits["LRU"],
            hits["LFU"],
            hits["DRRIP"],
        ]
    ]

    output("control", control_data)
    print("Did control")
    

    # Test different shapes of the input distribution
    shape_data = [["Shape var value", "LRU Hits", "LFU Hits", "DRRIP Hits"]]
    for shape in range(-100, 5, 25):
        row = [shape / 100]

        hits = benchmark([drrip, lfu, lru], shape=shape / 100)

        row += [
            round(hits["LRU"], ndigits=2),
            round(hits["LFU"], ndigits=2),
            round(hits["DRRIP"], ndigits=2),
        ]

        shape_data.append(row)

    output("shape", shape_data)
    print("Finished Shape Test")

    # Test different cache sizes
    cache_data = [["Cache Size", "LRU Hits", "LFU Hits", "DRRIP Hits"]]
    for exp in range(3, 14):
        size = 2**exp
        row = [size]

        hits = benchmark([drrip, lfu, lru], cache_size=size)

        row += [
            round(hits["LRU"], ndigits=2),
            round(hits["LFU"], ndigits=2),
            round(hits["DRRIP"], ndigits=2),
        ]

        cache_data.append(row)

    drrip.max_size = g_cache_size * g_requests
    lru.max_size = g_cache_size * g_requests
    lfu.max_size = g_cache_size * g_requests

    output("cache_size", cache_data)
    print("Finished cache size Test")

    # Test different number of lookups
    runs_data = [["Number of Lookups", "LRU Hits", "LFU Hits", "DRRIP Hits"]]
    for requests in range(1000, 11000, 1000):
        row = [requests]

        hits = benchmark([drrip, lfu, lru], requests=requests)

        row += [
            round(hits["LRU"], ndigits=2),
            round(hits["LFU"], ndigits=2),
            round(hits["DRRIP"], ndigits=2),
        ]

        runs_data.append(row)

    output("lookups", runs_data)
    print("Finished Lookups Test")


if __name__ == "__main__":
    test()
