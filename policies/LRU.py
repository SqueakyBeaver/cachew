import json
from functools import lru_cache
from .policy import Policy


class LRU(Policy):
    class CacheBlock:
        def __init__(self, tag: int, val: str, time: int):
            self.tag = tag
            self.val = val
            self.time = time

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache: list[list[LRU.CacheBlock]] = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0
        self.time = 0

    def __str__(self):
        return "LRU"

    def reset_cache(self) -> None:
        self.cache: list[list[LRU.CacheBlock]] = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0
        self.time = 0
    
    def evict(self, chunk: list[CacheBlock]):
        # min_time = float('inf')
        # evict_idx = 0
        # for (idx, block) in enumerate(self.cache[set_idx]):
        #     if block and block.time < min_time:
        #         min_time = block.time
        #         evict_idx = idx

        # self.cache[set_idx].pop(evict_idx)  
        # self.cache_size -= 1
        if chunk[0] is None:
            return 0
        
        lru = chunk[0]
        for (idx, block) in enumerate(chunk):
            if block is None:
                return idx
            
            if block.time < lru.time:
                self.cache_size -= 1
                return idx
        
        self.cache_size -= 1
        return 0


    def lookup(self, key: int) -> str:
        if self.cache_size > self.max_size:
            print("NONONO", str(self), self.cache_size)

        self.time += 1

        set_idx = key % self.num_sets
        tag = key // self.num_sets

        for idx, block in enumerate(self.cache[set_idx]):
            if block and block.tag == tag:
                self.add_hit()
                block.time = self.time

                return block.val

        replace_idx = self.evict(self.cache[set_idx])

        val = self.get_from_disk(tag)

        block = self.CacheBlock(tag, val, self.time)

        self.cache[set_idx][replace_idx] = block
        self.cache_size += 1

        return val
