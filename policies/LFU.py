import json
from .policy import Policy

class LFU(Policy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # { (uses, [keys] }
        self.cache_freq: dict[int, list[int]] = {}
        # { key: (uses, value) }
        self.cache: dict[int, tuple[int, str]] = {}

    def __str__(self):
        return "LFU"

    def lookup(self, key: int, fname: str) -> str:
        if len(self.cache) > self.max_size:
            print("NONONNONNONONNO")

        if key in self.cache:
            uses = self.cache[key][0]

            self.cache_freq[uses].pop(self.cache_freq[uses].index(key))

            if not self.cache_freq[uses]:
                self.cache_freq.pop(uses)

            if uses + 1 in self.cache_freq:
                self.cache_freq[uses + 1] += [key]
            else:
                self.cache_freq[uses + 1] = [key]

            val = self.cache[key][1]

            self.cache[key] = (uses + 1, val)

            return val

        uses = 1
        for freq, keys in self.cache_freq.items():
            if key in keys:
                uses = freq + 1
                keys.pop(keys.index(key))

                if len(keys) == 0:
                    self.cache_freq.pop(freq)
                break

        if len(self.cache) >= self.max_size:
            min_uses = min(self.cache.values())[0]

            least_used = self.cache_freq[min_uses]

            for i in least_used:
                if i in self.cache:
                    self.cache.pop(i)
            
            # Don't pop from cache_freq because
            # we still want to keep track of it for a bit

        val = self.getFromDisk(key, fname)

        if uses in self.cache_freq:
            self.cache_freq[uses] += [key]
        else:
            self.cache_freq[uses] = [key]

        self.cache[key] = (uses, val)

        return val
