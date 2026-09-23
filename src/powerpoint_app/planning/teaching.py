"""Persist teaching choices and reuse a small, cited set of design rules offline."""
from pathlib import Path

from powerpoint_app.domain.teaching import TeachingProfile
from powerpoint_app.projects.store import atomic_json

RULES_VERSION = "2026-09-23.1"
RULES = (
    ("visual_explanation", "Knyt korte forklaringer til mærkede figurer. Brug bevægelse kun når den forklarer en ændring.", "https://doi.org/10.1016/j.edurev.2025.100730"),
    ("worked_examples", "Vis korrekte mellemregninger før selvstændig øvelse ved nyt stof. Forklaringer skal være målrettede, ikke et spørgsmål ved hvert trin.", "https://doi.org/10.1007/s10648-023-09745-1"),
    ("transfer", "Tilpas eksempler og varierede øvelser til forkundskaber. Undgå et fast forhold mellem gennemgang og øvelse for alle emner.", "https://doi.org/10.1007/s10648-026-10169-w"),
    ("physical_model", "Forklar hvilket fysisk princip der bruges, hvordan det opstilles, og hvornår det gælder.", "https://doi.org/10.1103/PhysRevPhysEducRes.18.010136"),
)


def load_profile(root: Path) -> TeachingProfile | None:
    path = root / "teaching-profile.json"
    return TeachingProfile.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None


def save_profile(root: Path, profile: TeachingProfile) -> Path:
    target = root / "teaching-profile.json"
    atomic_json(target, profile.model_dump(mode="json"))
    return target


def teaching_brief(root: Path, brief: dict) -> dict:
    profile = load_profile(root)
    if not profile:
        return brief
    return {"audience": profile.audience, "duration_minutes": profile.duration_minutes,
            "approx_slides": profile.approximate_slides, **brief,
            "teaching_profile": profile.model_dump(mode="json")}


def teaching_instructions() -> str:
    return "\n".join([
        "UNDERVISNINGSREGLER " + RULES_VERSION,
        *[rule[1] for rule in RULES],
        "Hvis BRIEF har teaching_profile: brug schema_version 1.1 og kopiér profilen præcist.",
        "Hver slide får teaching.stage og objective_indices (0-baserede indeks i profilens læringsmål).",
        "Forbind praktisk udstyr, fysisk model og matematik. Bevar required_method og notation.",
        "Ved nyt stof: komplet regneeksempel, støttet øvelse og selvstændig anvendelse. Ved repetition: mere aktiv genkaldelse.",
        "Brug teaching.question til spørgsmål, svar og feedback. Læg aldrig svaret i titel eller elementer på spørgesliden.",
        "Beregn den samlede tid inklusive spørgsmål og afsløringer. Omtrentligt slideantal er antal logiske slides før trinvis eksport.",
        "Brug animations med on_click til formeltrin. Nødvendige givne værdier og figurer forbliver synlige.",
        "Knyt en grenformel til et parallel_circuit via diagram_id og branch_index (1-baseret). Den aktuelle gren fremhæves ved trinvis eksport.",
        "calculation_checks kan kontrollere numeriske udtryk med + - * / ** og simple SI-enheder. Det beviser ikke valg af fysisk model.",
        "Hvis materiale mangler, markér det i warnings. Ingen opdigtede tekniske data eller kilder.",
        "parallel_circuit er KUN en ideel DC-kilde og 2-4 parallelle modstande. Andre kredsløb må ikke forsimples til denne type.",
    ])
