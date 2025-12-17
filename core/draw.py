from typing import Dict, Any
from .prng import deterministic_shuffle

def run_draw(participants, seed: str, winners_count: int) -> Dict[str, Any]:
    if winners_count < 1:
        raise ValueError("winners_count must be >= 1")

    shuffled = deterministic_shuffle(participants, seed)
    winners = shuffled[:winners_count]

    return {
        "seed": seed,
        "total_participants": len(participants),
        "winners_count": winners_count,
        "shuffled": shuffled,
        "winners": winners
    }