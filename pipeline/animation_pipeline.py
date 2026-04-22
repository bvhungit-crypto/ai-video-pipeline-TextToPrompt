from __future__ import annotations

from core.camera_imperfection_engine import CameraImperfectionEngine
from core.clean_engine import CleanEngine
from core.environment_motion_engine import EnvironmentMotionEngine
from core.packaging_engine import PackagingEngine
from core.scene_analysis_engine import SceneAnalysisEngine
from core.style_presets import STYLE_PRESETS


class AnimationPipeline:
    def __init__(self, style: str = "2d_animation") -> None:
        self._packaging_engine = PackagingEngine()
        self._scene_analysis_engine = SceneAnalysisEngine()
        self.style_line = STYLE_PRESETS.get(style, STYLE_PRESETS["2d_animation"])
        self._clean_engine = CleanEngine()
        self._environment_motion_engine = EnvironmentMotionEngine()
        self._camera_imperfection_engine = CameraImperfectionEngine()

    def run(
        self,
        timeline: list[dict],
        style: str | None = None,
        mode: str | None = None,
    ) -> list[dict]:
        segments = self._packaging_engine.package(timeline)
        segments = self._scene_analysis_engine.analyze(segments)
        output: list[dict] = []
        used_motion_lines: set[str] = set()
        for index, seg in enumerate(segments):
            text = str(seg.get("text", "")).strip().lower()
            pose = self._pose_line(text, index)
            expression = self._expression_line(text, index)
            prompt = "\n\n".join(
                [
                    self._sentence(self.style_line),
                    self._sentence(pose),
                    self._sentence(expression),
                    "Simple background.",
                    "Duration: 6 seconds",
                ]
            )
            prompt = self._clean_engine.clean(prompt, has_character=True)
            prompt = self._camera_imperfection_engine.apply(prompt)
            prompt = self._environment_motion_engine.inject(prompt, used_lines=used_motion_lines)
            output.append({"start": seg["start"], "end": seg["end"], "prompt": prompt})
        return output

    @staticmethod
    def _pose_line(text: str, index: int) -> str:
        if any(word in text for word in ("run", "move", "walk")):
            return "Character pose: forward step with arms in motion"
        if any(word in text for word in ("sit", "desk", "table")):
            return "Character pose: seated posture with one hand on table"
        poses = (
            "Character pose: standing with balanced weight",
            "Character pose: slight lean with one arm raised",
            "Character pose: half-turn stance with relaxed shoulders",
        )
        return poses[index % len(poses)]

    @staticmethod
    def _expression_line(text: str, index: int) -> str:
        if any(word in text for word in ("happy", "smile", "joy")):
            return "Expression: soft smile with open eyes"
        if any(word in text for word in ("sad", "dark", "fear")):
            return "Expression: focused eyes with neutral mouth line"
        expressions = (
            "Expression: neutral face with attentive eyes",
            "Expression: light focus with calm brow",
            "Expression: thoughtful look with closed lips",
        )
        return expressions[index % len(expressions)]

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
