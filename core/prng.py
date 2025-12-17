from random import Random
from typing import List, Dict, Any

def deterministic_shuffle(participants: List[Dict[str, Any]], seed: str):
    rnd = Random(str(seed))
    copy = participants.copy()
    rnd.shuffle(copy)
    return copy
