import random
from .policy import Policy


class DRRIP(Policy):
    class CacheBlock:
        def __init__(self, tag: int, val: str, policy: str, rrpv: int = 3):
            self.tag = tag
            self.val = val
            self.rrpv = rrpv
            self.policy = policy

            if policy == "b":
                if random.random() <= 0.01:
                    self.rrpv = rrpv - 1

        def __str__(self):
            return f"({self.tag}, {self.val})"

    def __init__(self, max_rrpv=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_rrpv = max_rrpv

        self.cache: list[list[DRRIP.CacheBlock]] = [
            [None] * self.assoc for _ in range(self.num_sets)
        ]
        self.cache_size = 0

        self.s_idxs = set(random.sample(range(self.num_sets), self.num_sets // 4))

        self.b_idxs = set(
            random.sample(
                [i for i in range(self.num_sets) if not i in self.s_idxs],
                self.num_sets // 4,
            )
        )

        self.accesses = 0
        self.reset_interval = self.num_sets // 2
        self.policy_misses = {"s": 0, "b": 0}

    def __str__(self):
        return "DRRIP"

    def reset_cache(self) -> None:
        self.cache: list[list[DRRIP.CacheBlock]] = [
            [None] * self.assoc for _ in range(self.num_sets)
        ]
        self.cache_size = 0

        self.s_idxs = set(random.sample(range(self.num_sets), self.num_sets // 4))

        self.b_idxs = set(
            random.sample(
                [i for i in range(self.num_sets) if not i in self.s_idxs],
                self.num_sets // 4,
            )
        )

        self.accesses = 0
        self.policy_misses = {"s": 0, "b": 0}

    def evict(self, chunk: list[CacheBlock], policy: str) -> None:
        if chunk[0] is None:
            return 0

        while True:
            for idx, block in enumerate(chunk):
                if block is None:
                    return idx

                if block.rrpv >= self.max_rrpv:
                    self.cache_size -= 1
                    return idx

            for block in chunk:
                if block:
                    block.rrpv += 1

    def lookup(self, key: int) -> str:
        set_idx = key % self.num_sets
        tag = key // self.num_sets

        self.accesses += 1
        if self.accesses % self.reset_interval == 0:
            self.policy_misses = {"s": 0, "b": 0}

        for x in self.cache[set_idx]:
            if x and x.tag == tag:
                x.rrpv = 0
                self.add_hit()
                return x.val

        val = self.get_from_disk(tag)

        if set_idx in self.b_idxs:
            policy = "b"
        elif set_idx in self.s_idxs:
            policy = "s"
        else:
            policy = "b" if self.policy_misses["b"] < self.policy_misses["s"] else "s"

        block = self.CacheBlock(tag, val, policy)
        self.policy_misses[policy] += 1

        # if self.cache_size >= self.max_size:
        replace_idx = self.evict(self.cache[set_idx], policy)

        self.cache[set_idx][replace_idx] = block
        self.cache_size += 1

        return block.val
