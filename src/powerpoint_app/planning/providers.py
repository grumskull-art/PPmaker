from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProviderResult:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class Provider(Protocol):
    name: str
    model: str
    def complete(self, prompt: str) -> ProviderResult: ...


def _post(url: str, headers: dict[str, str], body: dict, timeout: int = 120) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str, endpoint: str = "http://127.0.0.1:11434"):
        self.model = model; self.endpoint = endpoint.rstrip("/")

    def complete(self, prompt: str) -> ProviderResult:
        data = _post(f"{self.endpoint}/api/generate", {}, {"model": self.model, "prompt": prompt, "stream": False, "format": "json"})
        return ProviderResult(data["response"], data.get("prompt_eval_count"), data.get("eval_count"))


class JsonApiProvider:
    """Opt-in OpenAI-compatible chat endpoint; the key is read only from an environment variable."""
    name = "api"

    def __init__(self, model: str, endpoint: str, key_env: str):
        self.model = model; self.endpoint = endpoint
        self.key = os.environ.get(key_env)
        if not self.key: raise ValueError(f"API-nøgle mangler i miljøvariablen {key_env}")

    def complete(self, prompt: str) -> ProviderResult:
        data = _post(self.endpoint, {"Authorization": f"Bearer {self.key}"}, {"model": self.model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}})
        usage = data.get("usage", {})
        return ProviderResult(data["choices"][0]["message"]["content"], usage.get("prompt_tokens"), usage.get("completion_tokens"))
