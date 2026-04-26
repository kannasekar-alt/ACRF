"""
Memory Guard - ACRF-04 defense layer.

Every memory entry is signed with HMAC-SHA256.
Before the agent acts on any memory entry, the signature is validated.
Tampered entries are rejected and flagged.

This implements ACRF-04 control objectives:
  MP-1: Memory namespace isolation
  MP-2: External inputs validated for contextual integrity
  MP-3: Memory tampering is detectable
"""
import hashlib
import hmac
import json

SECRET_KEY = b"acrf-04-memory-integrity-key-2026"

def sign_entry(entry: dict) -> str:
    canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    return hmac.new(SECRET_KEY, canonical.encode(), hashlib.sha256).hexdigest()

def verify_entry(entry: dict, signature: str) -> bool:
    expected = sign_entry(entry)
    return hmac.compare_digest(expected, signature)

def load_and_verify(memory_store_path: str) -> tuple[list, list]:
    with open(memory_store_path) as f:
        data = json.load(f)

    valid_users = []
    tampered_users = []

    for record in data["users"]:
        stored_sig = record.pop("_signature", None)
        if not stored_sig:
            tampered_users.append(record["user_id"])
            print(f"[MemoryGuard] ALERT: No signature found for {record['user_id']}")
            continue
        if verify_entry(record, stored_sig):
            valid_users.append(record)
        else:
            tampered_users.append(record["user_id"])
            print(f"[MemoryGuard] ALERT: TAMPERED entry detected for {record['user_id']}")
            print("[MemoryGuard] Entry rejected. Falling back to deny-by-default.")

    return valid_users, tampered_users
