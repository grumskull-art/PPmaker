from __future__ import annotations

import json

from powerpoint_app.domain.documents import Document

PROMPT_VERSION = "1.0"


def compact_prompt(documents: list[Document], brief: dict, schema: dict) -> str:
    source_payload = []
    for doc in documents:
        source_payload.append({
            "id": doc.source_id,
            "file": doc.file,
            "warnings": doc.warnings,
            "blocks": [vars(block) for block in doc.blocks],
        })
    return "\n".join([
        "Du er indholdsplanlægger for en dansk teknisk undervisningspræsentation.",
        "Returnér KUN gyldig JSON efter schemaet. Opfind ikke tal, svar eller kilder.",
        "Brug kun de tilladte layouts og elementtyper. Ingen kode, koordinater eller links.",
        "Markér antagelser og tvetydige formler. Bevar enheder, spørgsmål og notation.",
        f"PROMPT_VERSION={PROMPT_VERSION}",
        "BRIEF=" + json.dumps(brief, ensure_ascii=False),
        "SCHEMA=" + json.dumps(schema, ensure_ascii=False),
        "KILDER=" + json.dumps(source_payload, ensure_ascii=False),
    ])
