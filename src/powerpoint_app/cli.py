from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from powerpoint_app.domain.models import SlidePlan
from powerpoint_app.domain.teaching import TeachingProfile
from powerpoint_app.planning.teaching import load_profile, save_profile, teaching_brief
from powerpoint_app.rendering.teaching import presentation_frames
from powerpoint_app.importers import import_document
from powerpoint_app.office import add_animations
from powerpoint_app.planning import JsonApiProvider, OllamaProvider, compact_prompt, plan_with_provider
from powerpoint_app.projects import add_source, create_project, load_plan, safe_export_path, save_plan
from powerpoint_app.quality.checks import findings_json, inspect_plan
from powerpoint_app.rendering import PptxRenderer, load_theme


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="powerpoint-app", description="Lokal PowerPoint-app")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="opret projekt"); init.add_argument("project"); init.add_argument("--title", default="Nyt projekt")
    imp = sub.add_parser("import", help="kopiér og normalisér kilde"); imp.add_argument("project"); imp.add_argument("files", nargs="+")
    val = sub.add_parser("validate", help="validér slideplan"); val.add_argument("plan"); val.add_argument("--project", default=".")
    exp = sub.add_parser("export", help="eksportér PPTX uden LLM-kald"); exp.add_argument("project"); exp.add_argument("--plan"); exp.add_argument("--output", default="presentation.pptx"); exp.add_argument("--theme"); exp.add_argument("--animate", action="store_true")
    prm = sub.add_parser("prompt", help="lav kompakt prompt til valgfri chat"); prm.add_argument("project"); prm.add_argument("--topic", required=True); prm.add_argument("--audience", required=True); prm.add_argument("--minutes", type=int, default=None); prm.add_argument("--slides", type=int, default=None); prm.add_argument("--output", default="planning-prompt.txt")
    save = sub.add_parser("save-plan", help="validér og gem plan med historik"); save.add_argument("project"); save.add_argument("json_file")
    llm = sub.add_parser("plan", help="KONTAKTER LLM: opret plan via Ollama eller API")
    llm.add_argument("project"); llm.add_argument("--provider", choices=["ollama", "api"], required=True); llm.add_argument("--model", required=True); llm.add_argument("--endpoint"); llm.add_argument("--key-env", default="POWERPOINT_APP_API_KEY"); llm.add_argument("--topic", required=True); llm.add_argument("--audience", required=True); llm.add_argument("--minutes", type=int, default=None); llm.add_argument("--slides", type=int, default=None); llm.add_argument("--max-calls", type=int, default=2)
    profile = sub.add_parser("teaching", help="gem eller vis undervisningsprofil uden LLM")
    profile.add_argument("project"); profile.add_argument("--file", help="JSON-fil med TeachingProfile")
    exp.add_argument("--mode", choices=["auto", "static", "steps", "study"], default="auto")
    return p


def run(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "init":
        print(create_project(Path(args.project), args.title)); return 0
    if args.command == "teaching":
        root = Path(args.project)
        if not (root / "project.json").is_file(): raise ValueError("Opret eller åbn et projekt først.")
        if args.file:
            print(save_profile(root, TeachingProfile.model_validate_json(Path(args.file).read_text(encoding="utf-8"))))
        else:
            profile = load_profile(root)
            print(profile.model_dump_json(indent=2) if profile else "Ingen undervisningsprofil. Indlæs med --file profil.json.")
        return 0
    if args.command == "import":
        for filename in args.files:
            result = add_source(Path(args.project), Path(filename))
            print(f"{result['document'].source_id}: {result['stored_path']}")
            for warning in result["document"].warnings: print(f"ADVARSEL: {warning}", file=sys.stderr)
        return 0
    if args.command == "validate":
        plan = load_plan(Path(args.plan)); findings = inspect_plan(plan, Path(args.project))
        print(json.dumps(findings_json(findings), ensure_ascii=False, indent=2)); return 2 if any(x.level == "error" for x in findings) else 0
    if args.command == "save-plan":
        plan = load_plan(Path(args.json_file)); print(save_plan(Path(args.project), plan)); return 0
    if args.command == "prompt":
        root = Path(args.project); documents = []
        for source in sorted((root / "sources").iterdir()):
            if source.suffix.lower() in {".md", ".markdown", ".txt", ".docx", ".pdf"}:
                documents.append(import_document(source, f"src-{len(documents)+1}"))
        if not documents: raise ValueError("Projektet har ingen understøttede kilder.")
        brief = {"topic": args.topic, "audience": args.audience, **({"duration_minutes": args.minutes} if args.minutes is not None else {}), **({"approx_slides": args.slides} if args.slides is not None else {}), "language": "da", "output": "pptx"}
        brief = {"duration_minutes": 15, "approx_slides": 10, **teaching_brief(root, brief)}
        target = root / args.output; target.write_text(compact_prompt(documents, brief, SlidePlan.model_json_schema()), encoding="utf-8"); print(target); return 0
    if args.command == "plan":
        root = Path(args.project); documents = [import_document(path, f"src-{i+1}") for i, path in enumerate(sorted((root / "sources").iterdir())) if path.suffix.lower() in {".md", ".markdown", ".txt", ".docx", ".pdf"}]
        if not documents: raise ValueError("Projektet har ingen understøttede kilder.")
        brief = {"topic": args.topic, "audience": args.audience, **({"duration_minutes": args.minutes} if args.minutes is not None else {}), **({"approx_slides": args.slides} if args.slides is not None else {}), "language": "da", "output": "pptx"}
        brief = {"duration_minutes": 15, "approx_slides": 10, **teaching_brief(root, brief)}
        if args.provider == "ollama": provider = OllamaProvider(args.model, args.endpoint or "http://127.0.0.1:11434")
        else:
            if not args.endpoint: raise ValueError("--endpoint er påkrævet for API-provider.")
            provider = JsonApiProvider(args.model, args.endpoint, args.key_env)
        print("Sender kilder: " + ", ".join(doc.file for doc in documents), file=sys.stderr)
        plan, usage = plan_with_provider(root, documents, brief, provider, args.max_calls); save_plan(root, plan)
        print(json.dumps({"plan": str(root / "slide-plan.json"), "calls": usage.calls, "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "price": usage.price, "cache_hit": usage.cache_hit}, ensure_ascii=False)); return 0
    if args.command == "export":
        root = Path(args.project); plan = load_plan(Path(args.plan) if args.plan else root / "slide-plan.json")
        findings = inspect_plan(plan, root)
        if any(x.level == "error" for x in findings): raise ValueError("Eksport stoppet: " + "; ".join(x.message for x in findings if x.level == "error"))
        target = safe_export_path(root, args.output); theme = load_theme(Path(args.theme)) if args.theme else load_theme(root / "theme.json" if (root / "theme.json").exists() else None)
        if args.animate and (args.mode in {"steps", "study"} or plan.teaching_profile):
            raise ValueError("Brug trinvis eksport til undervisningsplaner. COM-animationer understøtter her kun almindelige planer med --mode static/auto.")
        PptxRenderer(root, theme).render(plan, target, mode=args.mode)
        print(f"Eksport: {len(plan.slides)} logiske slides, {len(presentation_frames(plan, args.mode))} slides i filen.", file=sys.stderr)
        if args.animate and any(s.animations for s in plan.slides):
            animated = target.with_name(f"{target.stem}-animated.pptx")
            add_animations(target, animated, plan); print(animated)
        else: print(target)
        return 0
    return 1


def main() -> None:
    try:
        raise SystemExit(run())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"FEJL: {exc}", file=sys.stderr); raise SystemExit(1)


if __name__ == "__main__":
    main()
