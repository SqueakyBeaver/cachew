import statistics
import random
import policies
import math
import itertools
from output import output

# Odd number means a nice, round median
g_reps = 1
g_requests = 100000
g_cache_size = 128

# Global so they will persist between runs
run_counter = 0
keyset = []


def zipf(num_unique: int, shape: float, request_count: int):
    norm_const = 1 / sum((i**shape for i in range(1, num_unique + 1)))

    def gen_elements():
        total = 0
        for i in range(num_unique):
            freq = norm_const * ((i + 1) ** shape)
            cnt = round(freq * request_count)
            total += cnt
            yield from itertools.repeat(i, cnt)

        if total < request_count:
            yield from itertools.repeat(0, request_count - total)

    ret = list(gen_elements())

    random.shuffle(ret)
    return ret


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
    global g_rng
    global keyset

    cache_size = math.floor(cache_size * requests)

    total_hits = {
        "LRU": [],
        "LFU": [],
        "RR": [],
    }
    for _ in range(g_reps):
        # Make a new keyset for each rep
        keyset = zipf(2 * cache_size, shape, requests)

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
        "RR": statistics.median(total_hits["RR"]),
    }


def test():
    global keyset
    global g_cache_size
    global g_requests

    lru = policies.LRU(max_size=g_cache_size)
    lfu = policies.LFU(max_size=g_cache_size)
    rr = policies.RR(max_size=g_cache_size)

    control_data = [["LRU Hits", "LFU Hits", "RR Hits"]]

    hits = benchmark([lru, lfu, rr])

    control_data += [
        [
            hits["LRU"],
            hits["LFU"],
            hits["RR"],
        ]
    ]

    output("control", control_data)
    print("Did control")

    # Test different shapes of the input distribution
    shape_data = [["Shape var value", "LRU Hits", "LFU Hits", "RR Hits"]]
    for shape in range(-100, 10, 25):
        row = [shape / 100]

        hits = benchmark([lru, lfu, rr], shape=shape / 100)

        row += [
            round(hits["LRU"], ndigits=2),
            round(hits["LFU"], ndigits=2),
            round(hits["RR"], ndigits=2),
        ]

        shape_data.append(row)

    output("shape", shape_data)
    print("Finished Shape Test")

    # Test different cache sizes
    cache_data = [["Cache Size", "LRU Hits", "LFU Hits", "RR Hits"]]
    for exp in range(5, 11):
        size = 2**exp
        print(size)
        row = [size]

        hits = benchmark([lru, lfu, rr], cache_size=size)

        row += [
            round(hits["LRU"], ndigits=2),
            round(hits["LFU"], ndigits=2),
            round(hits["RR"], ndigits=2),
        ]

        cache_data.append(row)

    rr.max_size = g_cache_size
    lru.max_size = g_cache_size
    lfu.max_size = g_cache_size

    output("cache_size", cache_data)
    print("Finished cache size Test")

    # Test different number of lookups
    runs_data = [["Number of Lookups", "LRU Hits (per 1000 Lookups)", "LFU Hits (per 1000 Lookups)", "RR Hits (per 1000 Lookups)"]]
    for requests in range(10000, 110000, 10000):
        row = [requests]

        hits = benchmark([lru, lfu, rr], requests=requests)

        row += [
            round(hits["LRU"] / (requests / 1000), ndigits=2),
            round(hits["LFU"] / (requests / 1000), ndigits=2),
            round(hits["RR"] / (requests / 1000), ndigits=2),
        ]

        runs_data.append(row)

    output("lookups", runs_data)
    print("Finished Lookups Test")


if __name__ == "__main__":
    test()
