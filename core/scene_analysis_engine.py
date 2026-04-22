from __future__ import annotations

import re


class SceneAnalysisEngine:
    def analyze(self, segments: list[dict]) -> list[dict]:
        for seg in segments:
            source = self._source_text(seg)
            lowered = source.lower()
            seg["has_human"] = self._has_human(lowered)
            seg["scene_type"] = self._scene_type(lowered)
            seg["objects"] = self._extract_objects(lowered)
            seg["environment"] = self._environment(lowered)
        return segments

    @staticmethod
    def _source_text(segment: dict) -> str:
        parts: list[str] = [str(segment.get("text", ""))]
        visual_plan = segment.get("visual_plan", {})
        if isinstance(visual_plan, dict):
            parts.append(str(visual_plan.get("subject", "")))
            details = visual_plan.get("details", [])
            if isinstance(details, list):
                parts.extend(str(item) for item in details)
        return " ".join(parts)

    @staticmethod
    def _has_human(text: str) -> bool:
        return bool(re.search(r"\b(person|people|man|woman|character|worker|face|hand|body)\b", text))

    @staticmethod
    def _scene_type(text: str) -> str:
        if "office" in text:
            return "office"
        if "street" in text or "road" in text or "city" in text:
            return "street"
        if any(word in text for word in ("room", "hallway", "factory", "indoor", "interior", "desk")):
            return "indoor"
        return "outdoor"

    @staticmethod
    def _extract_objects(text: str) -> list[str]:
        catalog = (
            "desk",
            "paper",
            "monitor",
            "chair",
            "table",
            "shelf",
            "window",
            "folder",
            "clock",
            "cable",
            "sign",
            "vehicle",
            "machine",
        )
        found = [word for word in catalog if re.search(rf"\b{re.escape(word)}\b", text)]
        return found[:5]

    @staticmethod
    def _environment(text: str) -> str:
        if any(word in text for word in ("street", "road", "city", "outdoor", "outside")):
            return "exterior"
        return "interior"
