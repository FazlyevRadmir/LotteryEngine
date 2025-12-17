import csv
import json
from typing import List, Dict, Any, Tuple

def load_participants_from_csv_fileobj(f) -> List[Dict[str, Any]]:
    text = f.read().decode('utf-8-sig')
    reader = csv.DictReader(text.splitlines())
    participants = [dict(r) for r in reader]

    if not participants and text.strip():
        for i, line in enumerate(text.splitlines()):
            participants.append({"id": str(i + 1), "name": line.strip()})

    return participants

def load_participants_from_json_fileobj(f) -> List[Dict[str, Any]]:
    data = json.load(f)
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be a list of participants")

def normalize_participants(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for i, p in enumerate(raw):
        if isinstance(p, dict):
            pid = p.get("id") or p.get("ID") or p.get("email") or str(i + 1)
            name = p.get("name") or p.get("fullname") or p.get("username") or pid
            new = {"id": str(pid), "name": str(name)}
            for k, v in p.items():
                if k not in ("id", "ID", "name", "fullname", "username"):
                    new[k] = v
            normalized.append(new)
        else:
            normalized.append({"id": str(i + 1), "name": str(p)})

    return normalized

def validate_participants(participants: List[Dict[str, Any]]) -> Tuple[bool, str]:
    if not participants:
        return False, "Список участников пуст"
    ids = [p["id"] for p in participants]
    if len(set(ids)) != len(ids):
        return False, "Повторяющиеся id участников"
    return True, "OK"
