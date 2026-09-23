from pathlib import Path

from powerpoint_app.domain.documents import Block, Document
from powerpoint_app.planning.providers import ProviderResult
from powerpoint_app.planning.service import plan_with_provider
from powerpoint_app.projects import create_project


VALID = '{"schema_version":"1.0","deck":{"title":"T","audience":"M","duration_minutes":2},"slides":[{"id":"s1","layout":"title","title":"T"}]}'


class FakeProvider:
    name = "fake"; model = "test"
    def __init__(self, answers): self.answers = iter(answers); self.calls = 0
    def complete(self, prompt): self.calls += 1; return ProviderResult(next(self.answers), 10, 5)


def test_one_schema_repair_then_cache(tmp_path: Path):
    create_project(tmp_path); doc = Document("src1", "a.md", "A", [Block("paragraph", "tekst", "linje 1")])
    provider = FakeProvider(["{}", VALID])
    plan, usage = plan_with_provider(tmp_path, [doc], {"topic": "T"}, provider, 2)
    assert plan.deck.title == "T" and usage.calls == 2
    cached, cached_usage = plan_with_provider(tmp_path, [doc], {"topic": "T"}, FakeProvider([]), 2)
    assert cached.deck.title == "T" and cached_usage.cache_hit
