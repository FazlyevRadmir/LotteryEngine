from typing import List, Dict, Any
from .draw import run_draw
from .participants import normalize_participants, validate_participants

def verify_draw(seed, participants_raw, winners_count, saved):
    normalized = normalize_participants(participants_raw)
    ok, msg = validate_participants(normalized)
    if not ok:
        return {"status": "INVALID", "reason": msg}

    recalculated = run_draw(normalized, seed, winners_count)

    saved_winners = saved["draw"]["winners"]
    saved_ids = [w["id"] for w in saved_winners]
    rec_ids = [w["id"] for w in recalculated["winners"]]

    return {
        "status": "VALID" if saved_ids == rec_ids else "INVALID",
        "saved_winner_ids": saved_ids,
        "recalculated_winner_ids": rec_ids
    }
