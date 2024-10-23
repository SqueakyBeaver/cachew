import timeit
import json
import random

#### TODO ####
# Make stuff being accessed more natural (weight towards some things, with lots of other little ones)
# Better benchmark function (tuned to pre-fill cache)


class LRU:
    def __init__(self):
        self.cache_keys: list[int] = []
        self.cache_vals: list[str] = []

        self.max_size = 10

        # Only count misses after the cache has been filled
        self.misses = -self.max_size

    # cache var is the filename of where to search
    def getFromDisk(self, key: int, fname: str) -> str:
        with open(fname) as file:
            loaded: dict[int, str] = json.load(file)

        return loaded.get(key)

    def lookup(self, key: int, fname: str) -> str:
        if key in self.cache_keys:
            # Find the old position of
            pos = self.cache_keys.index(key)

            # Move the key and vals to the front
            self.cache_keys.insert(0, key)
            self.cache_vals.insert(0, self.cache_vals[pos])

            # Pop the old values, these are now most recently used
            self.cache_keys.pop(pos + 1)
            self.cache_vals.pop(pos + 1)

            return self.cache_vals[0]

        # Cache miss
        self.misses += 1

        if len(self.cache_keys) >= self.max_size:
            # Replace
            self.cache_keys.pop()
            self.cache_vals.pop()

        val = self.getFromDisk(key, fname)

        self.cache_keys.insert(0, key)
        self.cache_vals.insert(0, val)

        return self.cache_vals[0]


class LFU:
    def __init__(self):
        # { (uses, [keys] }
        self.cache_freq: dict[int, list[int]] = {}
        # { key: (value, uses) }
        self.cache: dict[int, tuple[str, int]] = {}

        self.max_size = 10

        # Only count misses after the cache has been filled once
        self.misses = -self.max_size

    # cache var is the filename of where to search
    def getFromDisk(self, key: int, fname: str) -> str:
        with open(fname) as file:
            loaded: dict[int, str] = json.load(file)

        return loaded.get(key)

    def lookup(self, key: int, fname: str) -> str:
        if key in self.cache:
            uses = self.cache[key][1]

            self.cache_freq[uses].pop(self.cache_freq[uses].index(key))

            if not self.cache_freq[uses]:
                self.cache_freq.pop(uses)

            if uses + 1 in self.cache_freq:
                self.cache_freq[uses + 1] += [key]
            else:
                self.cache_freq[uses + 1] = [key]

            val = self.cache[key][0]

            self.cache[key] = (val, uses + 1)

            return val

        # Cache miss
        self.misses += 1

        uses = 1
        for freq, keys in self.cache_freq.items():
            if key in keys:
                uses = freq + 1
                keys.pop(keys.index(key))
                break

        if len(self.cache) >= self.max_size:
            least_used = self.cache_freq[min(self.cache_freq)][0]

            
            self.cache.pop(least_used, self.cache)
            # Don't pop from cache_freq because
            # we still want to keep track of it for a bit

        val = self.getFromDisk(key, fname)

        if uses in self.cache_freq:
            self.cache_freq[uses] += [key]
        else:
            self.cache_freq[uses] = [key]

        self.cache[key] = (val, uses)

        return val


runs = 100
lfu = LFU()
lru = LRU()
total_time = timeit.timeit(
    "lfu.lookup(random.randint(0, 32), 'inputs/small.json')",
    globals=globals(),
    number=runs,
)

total_time = timeit.timeit(
    "lru.lookup(random.randint(0, 32), 'inputs/small.json')",
    globals=globals(),
    number=runs,
)


print(f"{lfu.misses} misses using LFU")
print(f"{lru.misses} misses using LRU")
print(f"\n{total_time * 1000}ms taken total")
print(f"{total_time * 1000 / runs}ms taken on average")
