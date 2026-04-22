from __future__ import annotations

from core.packaging_engine import PackagingEngine
from core.prompt_engine import PromptEngine
from core.scene_engine import SceneEngine
from core.visual_planning_engine import VisualPlanningEngine


class DocumentaryPipeline:
    def __init__(self, style: str = "documentary", mode: str = "documentary") -> None:
        self._packaging_engine = PackagingEngine()
        self._visual_planning_engine = VisualPlanningEngine()
        self._scene_engine = SceneEngine()
        self._prompt_engine = PromptEngine(style=style, mode=mode)
        self.style = style
        self.mode = mode

    def run(
        self,
        timeline: list[dict],
        style: str | None = None,
        mode: str | None = None,
    ) -> list[dict]:
        segments = self._packaging_engine.package(timeline)
        segments = self._visual_planning_engine.plan(segments)
        segments = self._scene_engine.enhance(segments, mode=self.mode)
        return [
            {
                "start": seg["start"],
                "end": seg["end"],
                "prompt": self._prompt_engine.build(seg),
            }
            for seg in segments
        ]
