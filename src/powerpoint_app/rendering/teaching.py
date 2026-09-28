"""Presentation frames preserve geometry; later reveals never rearrange earlier objects."""
from dataclasses import dataclass

from powerpoint_app.domain.models import Slide, SlidePlan


@dataclass(frozen=True)
class Frame:
    slide: Slide
    hidden_ids: frozenset[str] = frozenset()
    show_answer: bool = False


def presentation_frames(plan: SlidePlan, mode: str = "auto") -> list[Frame]:
    if mode not in {"auto", "static", "steps", "study"}:
        raise ValueError("Ukendt eksportform.")
    if mode == "auto":
        mode = "steps" if plan.teaching_profile else "static"
    frames = []
    for slide in plan.slides:
        question = slide.teaching.question if slide.teaching else None
        if question:
            # Even static teaching exports give the audience time to answer.
            if mode != "study":
                frames.append(Frame(slide))
            frames.append(Frame(slide, show_answer=True))
        elif mode == "steps" and slide.animations:
            hidden = {a.target_id for a in slide.animations}
            ordered = sorted(slide.animations, key=lambda a: a.order)
            # Automatic events before the first click belong to the initial state.
            for index, animation in enumerate(ordered):
                if animation.trigger == "on_click":
                    frames.append(Frame(slide, frozenset(hidden)))
                hidden.discard(animation.target_id)
            frames.append(Frame(slide, frozenset(hidden)))
        else:
            frames.append(Frame(slide))
    return frames
