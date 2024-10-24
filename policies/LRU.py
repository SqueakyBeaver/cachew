import json

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
