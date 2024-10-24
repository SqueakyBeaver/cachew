import json

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

                if len(keys) == 0:
                    self.cache_freq.pop(freq)
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
