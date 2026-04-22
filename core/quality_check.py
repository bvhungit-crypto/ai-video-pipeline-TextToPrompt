from __future__ import annotations

import re


class QualityCheck:
    def is_bad(self, prompt: str) -> bool:
        sentences = self._sentences(prompt)
        content = [s for s in sentences if not s.lower().startswith("duration:")]
        if len(content) < 4:
            return True

        joined = " ".join(content).lower()
        has_environment = any(w in joined for w in ("room", "space", "hallway", "street", "office", "factory"))
        has_object = any(w in joined for w in ("desk", "paper", "table", "shelf", "chair", "window", "folder"))
        has_light = any(w in joined for w in ("light", "shadow", "reflection"))
        has_motion = any(w in joined for w in ("moves", "drift", "shift", "settle", "flicker", "sway"))

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
