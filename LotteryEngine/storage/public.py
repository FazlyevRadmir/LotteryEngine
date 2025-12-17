import os
import json
import uuid

PUBLIC_MAP_FILE = "results/public_map.json"

def register_public_token(rid: str) -> str:
    token = uuid.uuid4().hex
    mapping = {}

    if os.path.exists(PUBLIC_MAP_FILE):
        with open(PUBLIC_MAP_FILE, "r", encoding="utf-8") as f:
            mapping = json.load(f)

    mapping[token] = rid
    with open(PUBLIC_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    return token

def get_rid_by_token(token: str) -> str:
    if not os.path.exists(PUBLIC_MAP_FILE):
        raise KeyError

    with open(PUBLIC_MAP_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    if token not in mapping:
        raise KeyError

    return mapping[token]
