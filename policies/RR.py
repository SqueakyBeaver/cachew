import random
from .policy import Policy


class RR(Policy):
    class CacheBlock:
        def __init__(self, tag, val) -> None:
            self.tag = tag
            self.val = val

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0

    def __str__(self) -> str:
        return "RR"

    def reset_cache(self) -> None:
        self.cache = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0

    def evict(self, chunk: list[CacheBlock]) -> int:
        return random.randint(0, len(chunk) - 1)

    def lookup(self, key: int) -> str:
        set_idx = key % self.num_sets
        tag = key // self.num_sets

        for block in self.cache[set_idx]:
            if block and block.tag == tag:
                self.add_hit()
                return block.val
        
        replace_idx = self.evict(self.cache[set_idx])
        val = self.get_from_disk(tag)
        block = self.CacheBlock(tag, val)

        self.cache[set_idx][replace_idx] = block
        self.cache_size += 1

        return val

