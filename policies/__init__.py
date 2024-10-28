# This is just here so I can use policies.LRU and stuff
# :)
from .LFU import LFU
from .LRU import LRU
from .policy import Policy
from .DRRIP import DRRIP

__all__ = ["LFU", "LRU", "Policy", "DRRIP"]
