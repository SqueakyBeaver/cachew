# This is just here so I can use policies.LRU and stuff
# :)
from .LFU import LFU
from .LRU import LRU
from .policy import Policy
from .DRRIP import DRRIP
from .SRRIP import SRRIP

__all__ = ["LFU", "LRU", "Policy", "DRRIP", "SRRIP"]
