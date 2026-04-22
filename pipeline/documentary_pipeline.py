from __future__ import annotations

from core.camera_imperfection_engine import CameraImperfectionEngine
from core.clean_engine import CleanEngine
from core.environment_motion_engine import EnvironmentMotionEngine
from core.packaging_engine import PackagingEngine
from core.prompt_engine import PromptEngine
from core.scene_analysis_engine import SceneAnalysisEngine
from core.scene_engine import SceneEngine
from core.visual_planning_engine import VisualPlanningEngine


class DocumentaryPipeline:
    def __init__(self, style: str = "documentary", mode: str = "documentary") -> None:
        self._packaging_engine = PackagingEngine()
        self._visual_planning_engine = VisualPlanningEngine()
        self._scene_analysis_engine = SceneAnalysisEngine()
        self._scene_engine = SceneEngine()
        self._prompt_engine = PromptEngine(style=style, mode=mode)
        self._clean_engine = CleanEngine()
        self._environment_motion_engine = EnvironmentMotionEngine()
        self._camera_imperfection_engine = CameraImperfectionEngine()
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
        segments = self._scene_analysis_engine.analyze(segments)
        segments = self._scene_engine.enhance(segments, mode=self.mode)
        output: list[dict] = []
        used_motion_lines: set[str] = set()
        for seg in segments:
            prompt = self._prompt_engine.build(seg)
            has_character = self._has_character(seg.get("visual_plan", {}))
            prompt = self._clean_engine.clean(prompt, has_character=has_character)
            prompt = self._camera_imperfection_engine.apply(prompt)
            prompt = self._environment_motion_engine.inject(prompt, used_lines=used_motion_lines)
            output.append({"start": seg["start"], "end": seg["end"], "prompt": prompt})
        return output

    @staticmethod
    def _has_character(visual_plan: dict) -> bool:
        source = f"{visual_plan.get('subject', '')} {' '.join(visual_plan.get('details', []))}".lower()
        human_words = ("person", "people", "man", "woman", "character", "worker", "face", "hand")
        return any(word in source for word in human_words)
