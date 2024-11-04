import json
from .policy import Policy


class LFU(Policy):
    class CacheBlock:
        def __init__(self, tag: int, val: str, time: int):
            self.tag = tag
            self.val = val
            self.uses = 1
            self.time = time
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache: list[list[LFU.CacheBlock]] = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0
        self.time = 0

    def __str__(self):
        return "LFU"
    
    def reset_cache(self) -> None:
        self.cache: list[list[LFU.CacheBlock]] = [[None] * self.assoc for _ in range(self.num_sets)]
        self.cache_size = 0
        self.time = 0

    def evict(self, chunk: list[CacheBlock]) -> int:
        if chunk[0] is None:
            return 0
        
        lfu = chunk[0]
        lfu_idx = 0
        for (idx, block) in enumerate(chunk):
            if block is None:
                return idx
            
            if block.uses < lfu.uses:
                lfu = block
                lfu_idx = idx
            elif block.uses == lfu.uses:
                lfu = min(block, lfu, key=lambda x: x.time)
                lfu_idx = idx if lfu is block else lfu_idx

        self.cache_size -= 1
        return lfu_idx

    def lookup(self, key: int) -> str:
        if self.cache_size > self.max_size:
            print("NONONO", str(self))

        set_idx = key % self.num_sets
        tag = key // self.num_sets

        self.time += 1

        for block in self.cache[set_idx]:
            if block and block.tag == tag:
                self.add_hit()
                block.uses += 1
                return block.val
        
        val = self.get_from_disk(tag)

        block = self.CacheBlock(tag, val, self.time)

        replace_idx = self.evict(self.cache[set_idx])
        
        self.cache[set_idx][replace_idx] = block
        self.cache_size += 1

        return val
