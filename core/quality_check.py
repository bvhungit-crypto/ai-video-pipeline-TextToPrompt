from __future__ import annotations

import re


class QualityCheck:
    def is_bad(self, prompt: str) -> bool:
        sentences = self._sentences(prompt)
        content = [s for s in sentences if not s.lower().startswith("duration:")]
        if len(content) < 4:
            return True
        if self._has_list_style(content):
            return True

        joined = " ".join(content).lower()
        if any(word in joined for word in ("track", "reduce", "tighten", "focus", "balance shift")):
            return True
        has_environment = any(w in joined for w in ("room", "space", "hallway", "street", "office", "factory"))
        has_object = any(w in joined for w in ("desk", "paper", "table", "shelf", "chair", "window", "folder"))
        has_light = any(w in joined for w in ("light", "shadow", "reflection"))
        has_motion = any(w in joined for w in ("moves", "drift", "shift", "settle", "flicker", "sway"))
        if not self._has_flow_order(content):
            return True

        return not (has_environment and has_object and has_light and has_motion)

    @staticmethod
    def _sentences(prompt: str) -> list[str]:
        lines = [line.strip() for line in str(prompt).splitlines() if line.strip()]
        out: list[str] = []
        for line in lines:
            parts = re.split(r"(?<=[.!?])\s+", line)
            for part in parts:
                p = part.strip()
                if p:
                    out.append(p)
        return out

    @staticmethod
    def _has_list_style(content: list[str]) -> bool:
        short_count = sum(1 for s in content if len(s.split()) <= 5)
        comma_heavy = sum(1 for s in content if s.count(",") >= 2)
        return short_count >= 3 or comma_heavy >= 3

    @staticmethod
    def _has_flow_order(content: list[str]) -> bool:
        categories = []
        for sentence in content:
            lowered = sentence.lower()
            if any(w in lowered for w in ("room", "space", "hallway", "street", "office", "factory")):
                categories.append("environment")
            if any(w in lowered for w in ("light", "shadow", "reflection")):
                categories.append("light")
            if any(w in lowered for w in ("moves", "drift", "shift", "settle", "flicker", "sway")):
                categories.append("motion")
            if any(w in lowered for w in ("camera", "frame", "shot")):
                categories.append("camera")
        required = ["environment", "light", "motion", "camera"]
        indices = []
        for item in required:
            if item not in categories:
                return False
            indices.append(categories.index(item))
        return indices == sorted(indices)
