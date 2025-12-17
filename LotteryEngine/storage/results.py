import os
import json
import uuid
from typing import Dict, Any

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_result(draw_obj, checksum, metadata):
    rid = uuid.uuid4().hex
    container = {
        "id": rid,
        "checksum": checksum,
        "metadata": metadata,
        "draw": draw_obj
    }
    path = os.path.join(RESULTS_DIR, f"{rid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(container, f, ensure_ascii=False, indent=2)
    return rid

def load_result(rid: str) -> Dict[str, Any]:
    path = os.path.join(RESULTS_DIR, f"{rid}.json")
    if not os.path.exists(path):
        raise FileNotFoundError
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
