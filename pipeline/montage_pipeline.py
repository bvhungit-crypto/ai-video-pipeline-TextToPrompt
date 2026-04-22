from __future__ import annotations

from core.packaging_engine import PackagingEngine
from core.style_presets import STYLE_PRESETS


class MontagePipeline:
    def __init__(self, style: str = "documentary") -> None:
        self._packaging_engine = PackagingEngine()
        self.style_line = STYLE_PRESETS.get(style, STYLE_PRESETS["documentary"])

    def run(self, timeline: list[dict]) -> list[dict]:
        segments = self._packaging_engine.package(timeline)
        output: list[dict] = []
        for index, seg in enumerate(segments):
            place = self._place(seg.get("text", ""), index)
            detail = self._detail(index)
            motion = self._motion(index)
            prompt = "\n\n".join(
                [
                    self._sentence(self.style_line),
                    self._sentence(place),
                    self._sentence(detail),
                    self._sentence(motion),
                    "Duration: 6 seconds",
                ]
            )
            output.append({"start": seg["start"], "end": seg["end"], "prompt": prompt})
        return output

    @staticmethod
    def _place(text: str, index: int) -> str:
        lowered = str(text).lower()
        if "street" in lowered or "city" in lowered:
            variants = (
                "Street corner with buses and crosswalk lines",
                "Building entrance with glass doors and signboard",
                "Close view of wet pavement and shoe prints",
            )
            return variants[index % len(variants)]
        variants = (
            "Office room with desk, shelves, and paper files",
            "Hallway section with notice board and wall clock",
            "Close view of folder edges and handwritten notes",
        )
        return variants[index % len(variants)]

    @staticmethod
    def _detail(index: int) -> str:
        details = (
            "Metal frame, paper stacks, and cable lines are visible",
            "Glass reflections, wall marks, and taped labels are visible",
            "Dust on surfaces and worn paint texture are visible",
        )
        return details[index % len(details)]

    @staticmethod
    def _motion(index: int) -> str:
        motions = (
            "Quick cut with brief handheld movement",
            "Static hold with minor background motion",
            "Short pan across objects and surfaces",
        )
        return motions[index % len(motions)]

    @staticmethod
    def _sentence(value: str) -> str:
        cleaned = " ".join(str(value).strip().split()).strip(" ,;.")
        if not cleaned:
            return ""
        if cleaned.lower().startswith("duration:"):
            return cleaned
        if cleaned[-1] not in ".!?":
            cleaned += "."
        return cleaned
