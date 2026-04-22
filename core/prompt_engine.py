from __future__ import annotations

from typing import Any

from core.style_presets import STYLE_PRESETS


class PromptEngine:
    def __init__(self, style: str = "cinematic_dark", mode: str = "character") -> None:
        style_key = str(style).strip().lower() or "cinematic_dark"
        self.style_line = STYLE_PRESETS.get(style_key, STYLE_PRESETS["cinematic_dark"])
        self.mode = mode

    def build(self, segment: dict[str, Any]) -> str:
        visual_plan = segment.get("visual_plan", {})
        subject = self._clean_sentence(visual_plan.get("subject", "Office room with wooden desk and paper stacks"))
        details_items = visual_plan.get("details", [])
        details = self._details_line(details_items)
        environment = self._clean_sentence(visual_plan.get("environment", "Neutral indoor light"))
        camera_value = segment.get("camera", "medium")
        shot = self._shot_line(camera_value)
        motion = self._motion_for_shot(
            camera=camera_value,
            motion=visual_plan.get("motion", "minor background movement"),
            details=details_items,
            environment=visual_plan.get("environment", ""),
        )

        lines = [
            self._clean_sentence(self.style_line),
            subject,
            details,
            environment,
            shot,
            motion,
            "Duration: 6 seconds",
        ]
        deduped: list[str] = []
        seen: set[str] = set()
        for line in lines:
            key = line.lower()
            if not line or key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        return "\n\n".join(deduped)

    @staticmethod
    def _details_line(details: Any) -> str:
        if isinstance(details, list):
            parts = [str(item).strip() for item in details if str(item).strip()]
            if parts:
                unique_parts: list[str] = []
                seen: set[str] = set()
                for part in parts:
                    key = part.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    unique_parts.append(part)
                return PromptEngine._clean_sentence(", ".join(unique_parts))
        return "Wood desk surface, paper stack, and wall clock"

    @staticmethod
    def _shot_line(camera: Any) -> str:
        value = str(camera).strip().lower()
        if value == "wide":
            return "Wide shot, handheld camera"
        if value == "close":
            return "Close shot, handheld camera"
        return "Medium shot, handheld camera"

    @staticmethod
    def _motion_for_shot(camera: Any, motion: Any, details: Any, environment: Any) -> str:
        camera_value = str(camera).strip().lower()
        motion_text = " ".join(str(motion).strip().split()).lower()
        env_text = " ".join(str(environment).strip().split()).lower()
        detail_text = " ".join(str(item).strip().lower() for item in details) if isinstance(details, list) else ""

        if camera_value == "wide":
            if "rain" in env_text:
                return "Rain falls lightly across the window area."
            if "dust" in motion_text or "dust" in env_text:
                return "Dust particles are visible in the light beam."
            if "air" in motion_text or "curtain" in detail_text:
                return "Curtain moves slightly near the window."
            return "Light air movement is visible in the room."

        if camera_value == "close":
            if "paper" in detail_text:
                return "Paper edge lifts slightly."
            if "clip" in detail_text or "metal" in detail_text:
                return "Dust settles on the metal surface."
            if "ink" in detail_text:
                return "Paper corner shifts slightly."
            return "Small surface particles shift slightly."

        # Medium shot: motion must relate to objects in frame.
        if "paper" in detail_text or "folder" in detail_text:
            return "Top folder page moves slightly."
        if "screen" in detail_text or "monitor" in detail_text:
            return "Monitor reflection changes with minor camera movement."
        if "cable" in detail_text:
            return "Loose cable moves slightly near the desk edge."
        return "Small object movement is visible on the table."

    @staticmethod
    def _clean_sentence(value: Any) -> str:
        text = " ".join(str(value).strip().split()).strip(" ,;.")
        if not text:
            return ""
        if text.lower().startswith("duration:"):
            return text
        if text[-1] not in ".!?":
            text += "."
        return text
