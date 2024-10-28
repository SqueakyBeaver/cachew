import operator
import random
from .policy import Policy


class DRRIP(Policy):
    class CacheBlock:
        def __init__(self, key: int, val: str, policy: str, rrpv: int = 3):
            self.key = key
            self.val = val
            self.policy = policy

            p_bip = 0.05
            self.rrpv = (
                rrpv - 1 if policy == "BRRIP" and random.random() <= p_bip else rrpv
            )

        def __str__(self):
            return f"({self.key}, {self.val})"

    def __init__(self, max_rrpv=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_rrpv = max_rrpv

        self.num_chunks = self.max_size // 4

        # Divided into 4 chunks: [SRRIP],  [BRRIP], and the rest
        self.cache: list[list[DRRIP.CacheBlock]] = [list()] * self.num_chunks

        # BRRIP indexes
        self.b_sets = random.sample(range(self.max_size), self.num_chunks // 4)
        # SRRIP indexes
        self.s_sets = random.sample(range(self.max_size), self.num_chunks // 4)

        # BRRIP, SRRIP
        self.policy_cnt = [0, 0]

    def __str__(self):
        return "DRRIP"

    def evict(self, chunk: int) -> None:
        # No need to evict if the chunk isn't full
        if len(self.cache[chunk]) < self.max_size // self.num_chunks:
            return

        evict_idx = 0

        # Go through indexes
        # if chunk[idx].rrpv == max, that index is the new one to delete
        # If more than one max, delete oldest
        # If none, keep going

        while self.cache[chunk][evict_idx].rrpv < self.max_rrpv:
            for idx, block in enumerate(self.cache[chunk]):
                if block.rrpv == self.max_rrpv:
                    evict_idx = idx
                    break

                block.rrpv += 1

        # If the while loop never executed, then the oldest already has the max rrpv :)
        self.cache[chunk].pop(evict_idx)

    def lookup(self, key: int, fname: str) -> str:
        chunk = key % self.num_chunks

        x = None
        for x in self.cache[chunk]:
            if x and x.key == key:
                break
            else:
                x = None

        if x:
            # X is in cache
            x.rrpv = 0

            return x.val

        val = self.get_from_disk(key, fname)

        if chunk in self.b_sets:
            block = self.CacheBlock(key, val, "BRRIP")
        elif chunk in self.s_sets:
            block = self.CacheBlock(key, val, "SRRIP")
        else:
            policy = "BRRIP" if self.policy_cnt[0] > self.policy_cnt[1] else "SRRIP"
            block = self.CacheBlock(key, val, policy)

        if block.policy == "BRRP":
            self.policy_cnt[0] += 1
        else:
            self.policy_cnt[1] += 1

        self.evict(chunk)

        self.cache[chunk] += [block]

        for i in self.cache:
            print(len(i), sep=" ")
            for x in i:
                print(x, sep=" ")
            print()
        return block.val
