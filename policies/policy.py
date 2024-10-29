import math
from abc import ABC  # Abstract Base Class
import abc


class Policy(ABC):
    def __init__(self, max_size: int, assoc: int=4):
        self.max_size = max_size
        self.hits = []
        self.assoc = assoc
        self.num_sets = max_size // assoc

    def new_run(self):
        self.hits.append(0)
        self.reset_cache()
    
    def get_hits(self) -> int:
        return math.ceil(sum(self.hits) / len(self.hits))

    def add_hit(self):
        if len(self.hits) > 0:
            self.hits[-1] += 1
        else:
            self.hits.append(1)

    # cache var is the filename of where to search
    def get_from_disk(self, key: int) -> str:
        # Cache miss
        legend = "abcdefghijklmnopqrstuvwxyz"
        val = ""
        while True:
            val += legend[key % 26]
            key = key // 26

            if key == 0:
                return val

    @abc.abstractmethod
    def lookup(self, key: int) -> str:
        """
        Abstract method to lookup a val given a key.
        """
        pass

    @abc.abstractmethod
    def reset_cache(self) -> None:
        """
        Abstract method to reset the cache for a new run
        """
        pass
