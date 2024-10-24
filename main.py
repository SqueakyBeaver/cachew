import timeit
import random
import policies

runs = 1000
reps = 5

lfu = policies.LFU()
total_time = timeit.repeat(
    "lfu.lookup(random.randint(0, 255), 'inputs/small.json')",
    globals=globals(),
    repeat=reps,
    number=runs,
)
print(f"{lfu.misses} misses using LFU | {lfu.misses / (runs * reps) * 100}% missed")
print(f"{sum(total_time) * 1000}ms taken total")
print(f"Minimum time taken: {min(total_time) * 1000}ms\n")


lru = policies.LRU()
total_time = timeit.repeat(
    "lru.lookup(random.randint(0, 255), 'inputs/small.json')",
    globals=globals(),
    repeat=reps,
    number=runs,
)

print(f"{lru.misses} misses using LRU | {lru.misses / (runs * reps) * 100}% missed")
print(f"{sum(total_time) * 1000}ms taken total")
print(f"Minimum time taken: {min(total_time) * 1000}ms")
