from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from pydantic import ValidationError

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.planning.cache import cache_key
from powerpoint_app.planning.prompt import PROMPT_VERSION, compact_prompt
from powerpoint_app.projects.store import atomic_json


@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    price: str = "pris ukendt"
    cache_hit: bool = False


def plan_with_provider(project_root: Path, documents, brief: dict, provider, max_calls: int = 2) -> tuple[SlidePlan, Usage]:
    if max_calls < 1 or max_calls > 3:
        raise ValueError("Kald-budget skal være mellem 1 og 3.")
    raw_docs = [doc.to_dict() for doc in documents]
    key = cache_key(raw_docs, brief, provider.name, provider.model, PROMPT_VERSION, "1.0")
    cache = project_root / "cache" / f"plan-{key}.json"
    usage_path = project_root / "cache" / f"plan-{key}-usage.json"
    if cache.exists():
        usage = Usage(**json.loads(usage_path.read_text(encoding="utf-8"))) if usage_path.exists() else Usage()
        usage.cache_hit = True
        return SlidePlan.model_validate_json(cache.read_text(encoding="utf-8")), usage
    prompt = compact_prompt(documents, brief, SlidePlan.model_json_schema())
    usage = Usage()
    result = provider.complete(prompt); usage.calls += 1; usage.input_tokens += result.input_tokens or 0; usage.output_tokens += result.output_tokens or 0
    try:
        plan = SlidePlan.model_validate_json(result.text)
    except ValidationError as exc:
        if usage.calls >= max_calls:
            raise ValueError(f"Providerens JSON passer ikke til schemaet: {exc}") from exc
        repair = "Ret KUN JSON-dokumentet efter fejlene. Bevar fagligt indhold og returnér kun JSON.\nFEJL=" + str(exc) + "\nJSON=" + result.text
        result = provider.complete(repair); usage.calls += 1; usage.input_tokens += result.input_tokens or 0; usage.output_tokens += result.output_tokens or 0
        plan = SlidePlan.model_validate_json(result.text)
    atomic_json(cache, plan.model_dump(mode="json")); atomic_json(usage_path, asdict(usage))
    return plan, usage
