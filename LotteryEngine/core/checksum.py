import json
import hashlib
from typing import List, Dict, Any

def participants_checksum(participants: List[Dict[str, Any]]) -> str:
    sorted_p = sorted(participants, key=lambda x: x["id"])
    b = json.dumps(sorted_p, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(b).hexdigest()
