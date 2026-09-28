"""Regenerate the bounded BM4 exam lesson from the verified circuit model."""
import json
from pathlib import Path

from powerpoint_app.domain.models import SlidePlan, ThreeSourceCircuitElement
from powerpoint_app.quality.three_source_dc import circuit_quantities, solve_three_source_dc


ROOT = Path(__file__).resolve().parent
CIRCUIT = ThreeSourceCircuitElement(
    id="reference", type="three_source_dc", sources=(50, 30, 25),
    resistances=(25, 27, 15, 10, 8), source_ids=["exam"],
)
SOLUTION = solve_three_source_dc(CIRCUIT)
VALUES = circuit_quantities(CIRCUIT)


def diagram(name):
    return {**CIRCUIT.model_dump(mode="json"), "id": name}


def formula(name, latex, diagram_id=None, branch_index=None):
    result = {"id": name, "type": "formula", "latex": latex, "source_ids": ["exam"]}
    if diagram_id:
        result.update(diagram_id=diagram_id, branch_index=branch_index)
    return result


def calculation(name, expression, variables, result, unit, diagram_id):
    return {
        "element_id": name, "diagram_id": diagram_id, "expression": expression,
        "quantities": {key: {"value": VALUES[key][0], "unit": VALUES[key][1]} for key in variables},
        "expected": {"value": result, "unit": unit},
    }


def slide(name, title, layout, stage, goals, elements, seconds, notes, *, checks=(), question=None, steps=False):
    animations = [
        {"target_id": e["id"], "order": index, "trigger": "on_click"}
        for index, e in enumerate(elements, 1) if e["type"] == "formula"
    ] if steps else []
    return {
        "id": name, "title": title, "layout": layout,
        "objective": "Forklar opgavens fysik og regnemetode.", "elements": elements,
        "speaker_notes": notes, "estimated_seconds": seconds,
        "animations": animations, "calculation_checks": list(checks),
        "teaching": {
            "stage": stage, "objective_indices": goals,
            "assumptions": ["Ideelle kilder og ledninger, konstante modstande, stationær DC-tilstand."],
            **({"question": question} if question else {}),
        },
    }


def build():
    slides = [
        slide("s1", "Tre kilder forsyner fem modstande", "key_figure", "context", [0],
              [diagram("c1"), {"id": "t1", "type": "text", "text":
               "Pilene I1–I5 viser valgte positive strømretninger. Find strømmene, U_AB og samlet effekt.", "source_ids": ["exam"]}],
              70, "Topologi og kildepoler er tegnet efter originalarket. Gengiv ikke de ældre ChatGPT-tegninger."),
        slide("s2", "C er referencepunktet 0 V", "key_figure", "model", [0, 1],
              [diagram("c2"), {"id": "t2", "type": "text", "text":
               "L er knuden før R1; B er knuden efter R5. Med C = 0 V: V_L = 50 V og V_B = 30 V.", "source_ids": ["exam"]}],
              85, "L betyder venstre knude; B er målepunktet fra U_AB. C = 0 V er et referencevalg. E1 har plus mod L; E2 og E3 har plus mod højre."),
        slide("s3", "KCL i A forbinder tre grene", "formula_steps", "worked_example", [0],
              [diagram("c3"), formula("f31", r"I_1=I_2+I_3"),
               formula("f32", r"\frac{V_A-50}{25}+\frac{V_A}{27}+\frac{V_A-V_D+25}{15}=0")],
              110, "Vis strømmenes valgte retninger; omregn KCL til knudepotentialer.", steps=True),
        slide("s4", "E3 indgår i KCL ved D", "formula_steps", "worked_example", [0],
              [diagram("c4"), formula("f41", r"I_4=I_3+I_5"),
               formula("f42", r"\frac{V_D-V_A-25}{15}+\frac{V_D}{10}+\frac{V_D-30}{8}=0")],
              100, "E3 er positiv ved D. Brug superknude eller eliminér potentialet mellem R3 og E3.", steps=True),
        slide("s5", "To potentialer giver U_AB med fortegn", "formula_steps", "worked_example", [0, 1],
              [diagram("c5"), formula("f51", r"V_A=12.2323\,\mathrm{V}"),
               formula("f52", r"V_D=21.3674\,\mathrm{V}"),
               formula("f53", r"U_{AB}=V_A-V_B=12.2323-30=-17.7677\,\mathrm{V}")],
              100, "Løs de to lineære ligninger. B = 30 V, så V_A - V_B er negativ.",
              checks=[calculation("f51", "VA", ["VA"], SOLUTION.va, "V", "c5"),
                      calculation("f52", "VD", ["VD"], SOLUTION.vd, "V", "c5"),
                      calculation("f53", "VA-VB", ["VA", "VB"], SOLUTION.vab, "V", "c5")], steps=True),
    ]

    current_formulas = [
        (r"I_1=\frac{50-V_A}{25}=1.5107\,\mathrm{A}", "(E1-VA)/R1", ["E1", "VA", "R1"]),
        (r"I_2=\frac{V_A}{27}=0.4530\,\mathrm{A}", "VA/R2", ["VA", "R2"]),
        (r"I_3=\frac{V_A-V_D+25}{15}=1.0577\,\mathrm{A}", "(VA-VD+E3)/R3", ["VA", "VD", "E3", "R3"]),
        (r"I_4=\frac{V_D}{10}=2.1367\,\mathrm{A}", "VD/R4", ["VD", "R4"]),
        (r"I_5=\frac{30-V_D}{8}=1.0791\,\mathrm{A}", "(E2-VD)/R5", ["E2", "VD", "R5"]),
    ]
    slides.append(slide("s6", "Fem strømme følger fem valgte retninger", "formula_steps", "worked_example", [0],
                        [diagram("c6")] + [formula(f"f6{i}", item[0], "c6", i) for i, item in enumerate(current_formulas, 1)],
                        125, "Fremhæv den tilhørende modstand. I4 går D til C; I5 går B til D.",
                        checks=[calculation(f"f6{i}", item[1], item[2], SOLUTION.currents[i-1], "A", "c6")
                                for i, item in enumerate(current_formulas, 1)], steps=True))
    slides.append(slide("s7", "Hvad viser voltmeteret mellem A og B?", "two_columns", "retrieval", [1],
                        [diagram("c7")], 70, "Rød probe ved A og sort ved B. Lad deltagerne svare før afsløring.",
                        question={"prompt": "Hvad viser voltmeteret med rød probe i A og sort i B?",
                                  "answer": "U_AB = -17,77 V.",
                                  "explanation": "A er ca. 12,23 V og B er 30 V, så V_A - V_B er negativ.",
                                  "wait_seconds": 30, "options": ["-17,77 V", "+17,77 V", "0 V"],
                                  "correct_option": 0,
                                  "discussion_prompt": "Forklar referencepunkt og probernes rækkefølge for din makker."}))

    slides.append(slide("s8", "Hver modstand afgiver I²R som varme", "formula_steps", "worked_example", [2],
                        [diagram("c8")] + [formula(f"f8{i}", rf"P_{i}=R_{i}I_{i}^2={power:.3f}\,\mathrm{{W}}", "c8", i)
                                           for i, power in enumerate(SOLUTION.resistor_powers, 1)],
                        120, "Regn med fuld præcision; R5 er 8 Ω. Kontrollér alle fem effekter før summen.",
                        checks=[calculation(f"f8{i}", f"R{i}*I{i}**2", [f"R{i}", f"I{i}"],
                                            power, "W", "c8")
                                for i, power in enumerate(SOLUTION.resistor_powers, 1)], steps=True))
    slides.append(slide("s9", "De fem modstande bruger tilsammen 134,35 W", "formula_steps", "summary", [2],
                        [diagram("c9"),
                         formula("f91", r"P_{\mathrm{samlet}}=\sum_{k=1}^{5}R_k I_k^2=134.349\,\mathrm{W}"),
                         formula("f92", r"P_{\mathrm{kilder}}=E_1I_1+E_2I_5+E_3I_3=134.349\,\mathrm{W}")],
                        70, "Summen fra modstandene er lig effekten fra de tre ideelle kilder.",
                        checks=[calculation("f91", "P1+P2+P3+P4+P5", ["P1", "P2", "P3", "P4", "P5"],
                                            SOLUTION.total_power, "W", "c9"),
                                calculation("f92", "E1*I1+E2*I5+E3*I3", ["E1", "I1", "E2", "I5", "E3", "I3"],
                                            SOLUTION.total_power, "W", "c9")], steps=True))

    profile = {
        "profile_version": "1.0", "subject": "Jævnstrøm, MARTEC F2023 opgave 3",
        "audience": "Maskinmesterstuderende BM4",
        "prior_knowledge": ["Ohms lov", "Kirchhoffs 1. lov", "Spænding som potentialforskel"],
        "learning_objectives": ["Find fem grenstrømme med valgte retninger.",
                                "Bestem U_AB med fortegn og forklar målingen.",
                                "Beregn effektforbruget og kontrollér effektbalancen."],
        "required_method": "Knudepotentialer og KCL. Ingen krav om maskestrømme.",
        "notation": ["C = 0 V", "E1 plus ved L; E2 og E3 plus mod højre",
                     "I1 L→A, I2 A→C, I3 A→D, I4 D→C, I5 B→D", "U_AB = V_A - V_B"],
        "support": "guided", "duration_minutes": 15, "approximate_slides": len(slides),
    }
    plan = SlidePlan.model_validate({
        "schema_version": "1.1",
        "deck": {"title": "BM4 opgave 3: tre kilder og fem modstande", "language": "da",
                 "audience": profile["audience"], "duration_minutes": 15},
        "teaching_profile": profile,
        "sources": [{"id": "exam", "file": "sources/exercise.md", "locator": "Topologi og tal fra F2023 opgave 3"}],
        "slides": slides,
    })
    (ROOT / "project.json").write_text(json.dumps({"format_version": "1.0", "title": "BM4 F2023 opgave 3"}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (ROOT / "teaching-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (ROOT / "slide-plan.json").write_text(plan.model_dump_json(indent=2)+"\n", encoding="utf-8")
    return plan


if __name__ == "__main__":
    print(f"Generated {len(build().slides)} logical slides in {ROOT}")
