import json
from functools import lru_cache
from .policy import Policy


class LRU(Policy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_keys: list[int] = []
        self.cache_vals: list[str] = []

    def __str__(self):
        return "LRU"

    def reset_cache(self) -> None:
        self.cache_keys: list[int] = []
        self.cache_vals: list[str] = []

    def lookup(self, key: int, fname: str) -> str:
        if key in self.cache_keys:
            # Find the old position
            pos = self.cache_keys.index(key)

            # Move the key and vals to the front
            self.cache_keys.insert(0, key)
            self.cache_vals.insert(0, self.cache_vals[pos])

            # Pop the old values, these are now most recently used
            self.cache_keys.pop(pos + 1)
            self.cache_vals.pop(pos + 1)

            return self.cache_vals[0]

        if (
            len(self.cache_vals) >= self.max_size
            or len(self.cache_keys) >= self.max_size
        ):
            # Replace
            self.cache_keys.pop()
            self.cache_vals.pop()

        val = self.get_from_disk(key, fname)

        self.cache_keys.insert(0, key)
        self.cache_vals.insert(0, val)

        return self.cache_vals[0]
