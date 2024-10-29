import random
from .policy import Policy


class DRRIP(Policy):
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

        self.cache: list[list[DRRIP.CacheBlock]] = [[] for i in range(self.num_chunks)]
        self.cache_size = 0

        self.s_idxs = random.sample(
            range(self.max_size), self.max_size // self.num_chunks
        )

        self.b_idxs = random.sample(
            [i for i in range(self.max_size) if not i in self.s_idxs],
            self.max_size // self.num_chunks,
        )

        self.policy_misses = {"s": 0, "b": 0}

    def __str__(self):
        return "DRRIP"

    def reset_cache(self) -> None:
        self.cache: list[list[DRRIP.CacheBlock]] = [[] for i in range(self.num_chunks)]
        self.cache_size = 0
        self.policy_misses = {"s": 0, "b": 0}


    def evict(self, chunk: int, policy: str) -> None:
        while len(self.cache[chunk]) == 0:
            chunk = (chunk + 1) % self.num_chunks
        
        self.policy_misses[policy] -= 1

        self.cache_size -= 1

        evict_idx = 0
        while self.cache[chunk][evict_idx].rrpv < self.max_rrpv:
            for idx, block in enumerate(self.cache[chunk]):
                if block and block.rrpv >= self.max_rrpv:
                    self.cache[chunk].pop(idx)
                    return

            for block in self.cache[chunk]:
                if block:
                    block.rrpv += 1

        # If the while loop never executed, then the oldest already has the max rrpv :)
        self.cache[chunk].pop(evict_idx)

    def lookup(self, key: int, fname: str) -> str:
        if self.cache_size > self.max_size:
            print("NONONONNNNONONNO")
        chunk = key % self.num_chunks
        # The index that the key would occupy if the list was flattened
        real_idx = key % self.max_size

        for x in self.cache[chunk]:
            if x and x.key == key:
                x.rrpv = 0

                return x.val

        val = self.get_from_disk(key, fname)

        if real_idx in self.b_idxs:
            policy = "b"
        elif real_idx in self.s_idxs:
            policy = "s"
        else:
            policy = "b" if self.policy_misses["b"] < self.policy_misses["s"] else "s"

        block = self.CacheBlock(key, val, policy)
        self.policy_misses[policy] += 1

        if self.cache_size >= self.max_size:
            self.evict(chunk, policy)

        self.cache[chunk].append(block)
        self.cache_size += 1

        return block.val
