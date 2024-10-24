import timeit
import random
import policies

runs = 100

lfu = policies.LFU()
total_time = timeit.timeit(
    "lfu.lookup(random.randint(0, 100), 'inputs/small.json')",
    globals=globals(),
    number=runs,
)
print(f"{lfu.misses} misses using LFU | {lfu.misses / runs * 100}% missed")
print(f"{total_time * 1000}ms taken total")
print(f"{total_time * 1000 / runs}ms taken on average\n")


lru = policies.LRU()
total_time = timeit.timeit(
    "lru.lookup(random.randint(0, 32), 'inputs/small.json')",
    globals=globals(),
    number=runs,
)

print(f"{lru.misses} misses using LRU | {lru.misses / runs * 100}% missed")
print(f"{total_time * 1000}ms taken total")
print(f"{total_time * 1000 / runs}ms taken on average")
