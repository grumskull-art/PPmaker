from __future__ import annotations

import hashlib
import json


def cache_key(documents: list[dict], brief: dict, provider: str, model: str, prompt_version: str, schema_version: str) -> str:
    payload = {"documents": documents, "brief": brief, "provider": provider, "model": model,
               "prompt_version": prompt_version, "schema_version": schema_version}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()
