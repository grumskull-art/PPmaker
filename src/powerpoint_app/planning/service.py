from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from pydantic import ValidationError

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.planning.cache import cache_key
from powerpoint_app.planning.prompt import PROMPT_VERSION, compact_prompt
from powerpoint_app.projects.store import atomic_json
from powerpoint_app.planning.teaching import teaching_brief


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
    brief = teaching_brief(project_root, brief)
    raw_docs = [doc.to_dict() for doc in documents]
    key = cache_key(raw_docs, brief, provider.name, provider.model, PROMPT_VERSION, "1.1")
    cache = project_root / "cache" / f"plan-{key}.json"
    usage_path = project_root / "cache" / f"plan-{key}-usage.json"
    if cache.exists():
        usage = Usage(cache_hit=True)
        return SlidePlan.model_validate_json(cache.read_text(encoding="utf-8")), usage
    def validate_response(payload):
        candidate = SlidePlan.model_validate_json(payload)
        if "teaching_profile" in brief:
            if candidate.teaching_profile is None or candidate.teaching_profile.model_dump(mode="json") != brief["teaching_profile"]:
                raise ValueError("Providerens teaching_profile skal svare præcist til brugerens profil.")
            if any(slide.teaching is None for slide in candidate.slides):
                raise ValueError("Alle slides skal angive teaching.stage og objective_indices.")
        return candidate

    prompt = compact_prompt(documents, brief, SlidePlan.model_json_schema())
    usage = Usage()
    result = provider.complete(prompt); usage.calls += 1; usage.input_tokens += result.input_tokens or 0; usage.output_tokens += result.output_tokens or 0
    try:
        plan = validate_response(result.text)
    except (ValidationError, ValueError) as exc:
        if usage.calls >= max_calls:
            raise ValueError(f"Providerens JSON passer ikke til schemaet: {exc}") from exc
        repair = "BRIEF=" + json.dumps(brief, ensure_ascii=False) + "\nRet KUN JSON-dokumentet efter fejlene. Bevar fagligt indhold og returnér kun JSON.\nFEJL=" + str(exc) + "\nJSON=" + result.text
        result = provider.complete(repair); usage.calls += 1; usage.input_tokens += result.input_tokens or 0; usage.output_tokens += result.output_tokens or 0
        plan = validate_response(result.text)
    atomic_json(cache, plan.model_dump(mode="json")); atomic_json(usage_path, asdict(usage))
    return plan, usage
