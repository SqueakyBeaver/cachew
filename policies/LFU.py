import json
from .policy import Policy


class LFU(Policy):
    class CacheBlock:
        def __init__(self, key, val):
            self.key = key
            self.val = val
            self.uses = 1    
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache: list[LFU.CacheBlock] = []

    def __str__(self):
        return "LFU"
    
    def reset_cache(self) -> None:
        self.cache: list[LFU.CacheBlock] = []

    def lookup(self, key: int) -> str:
        for block in self.cache:
            if block and block.key == key:
                # Cache Hit
                block.uses += 1
                return block.val
        
        val = self.get_from_disk(key)

        block = self.CacheBlock(key, val)

        if len(self.cache) >= self.max_size:
            to_evict = min(self.cache, key=lambda x: x.uses)
            self.cache.pop(self.cache.index(to_evict))
        
        self.cache.append(block)

        return val
