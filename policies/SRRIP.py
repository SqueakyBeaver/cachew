import random
from .policy import Policy


class SRRIP(Policy):
    class CacheBlock:
        def __init__(self, key: int, val: str, policy: str, rrpv: int = 3):
            self.key = key
            self.val = val
            self.rrpv = rrpv
            self.policy = policy

            if policy == "b":
                if random.random() <= 0.01:
                    self.rrpv = rrpv - 1

        def __str__(self):
            return f"({self.key}, {self.val})"

    def __init__(self, num_chunks=4, max_rrpv=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_rrpv = max_rrpv

        self.num_chunks = num_chunks

        self.cache: set[SRRIP.CacheBlock] = set()
        self.cache_size = 0

    def __str__(self):
        return "DRRIP"

    def reset_cache(self) -> None:
        # Make this a set with simulated s and b indexes or something
        # Either that or do an SRRIP type thing
        self.cache: list[SRRIP.CacheBlock] = []
        self.cache_size = 0

    def evict(self) -> None:
        if len(self.cache) < self.max_size:
            return
        
        self.cache_size -=1

        evict_idx = 0
        while self.cache[evict_idx].rrpv < self.max_rrpv:
            for idx, block in enumerate(self.cache):
                if block and block.rrpv >= self.max_rrpv:
                    self.cache.pop(idx)
                    return

            for block in self.cache:
                if block:
                    block.rrpv += 1

        # If the while loop never executed, then the oldest already has the max rrpv :)
        self.cache.pop(evict_idx)

    def lookup(self, key: int) -> str:
        for x in self.cache:
            if x and x.key == key:
                x.rrpv = 0
                self.add_hit()
                return x.val

        val = self.get_from_disk(key)

        policy = "b"

        block = self.CacheBlock(key, val, policy)

        if self.cache_size >= self.max_size:
            self.evict()

        self.cache.append(block)
        self.cache_size += 1

        return block.val
