import json
from abc import ABC # Abstract Base Class
import abc

class Policy(ABC):
    def __init__(self, max_size):
        self.max_size = max_size
        self.misses = 0

    # cache var is the filename of where to search
    def getFromDisk(self, key: int, fname: str) -> str:
        # Cache miss
        self.misses += 1

        with open(fname) as file:
            loaded: dict[int, str] = json.load(file)

        return loaded.get(str(key % len(loaded)))
    
    @abc.abstractmethod
    def lookup(self, key: int, fname: str) -> str:
        '''Override me'''
        pass