import math
from abc import ABC  # Abstract Base Class
import abc


class Policy(ABC):
    def __init__(self, max_size):
        self.max_size = max_size
        self.misses = []

    def new_run(self):
        self.misses.append(0)
        self.reset_cache()
    
    def get_misses(self) -> int:
        return math.ceil(sum(self.misses) / len(self.misses))

    # cache var is the filename of where to search
    def get_from_disk(self, key: int) -> str:
        # Cache miss
        self.misses[-1] += 1

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
