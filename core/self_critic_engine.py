from __future__ import annotations

import re


class SelfCriticEngine:
    ABSTRACT_WORDS = ("balance", "tension", "focus")
    CAMERA_INTENT_WORDS = ("track", "reduce", "tighten", "follow")
    HUMAN_WORDS = ("she", "he", "person", "man", "woman", "character", "hand", "jaw", "shoulder", "breath")
    ENVIRONMENT_WORDS = ("room", "desk", "space")
    MOTION_WORDS = ("move", "shift", "drift", "lift")

    def evaluate(self, prompt: str, segment: dict) -> dict:
        text = str(prompt or "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lower = text.lower()
        issues: list[str] = []

        if len(lines) < 5:
            issues.append("too_short")

        if self._has_duplicate_lines(lines):
            issues.append("duplicate_lines")

        if any(word in lower for word in self.ABSTRACT_WORDS):
            issues.append("abstract_words")

        if any(word in lower for word in self.CAMERA_INTENT_WORDS):
            issues.append("camera_intent_words")

        has_character = self._has_character(segment)
        if not has_character and any(word in lower for word in self.HUMAN_WORDS):
            issues.append("human_words_no_character")

        if not any(word in lower for word in self.ENVIRONMENT_WORDS):
            issues.append("missing_environment")

        if not any(word in lower for word in self.MOTION_WORDS):
            issues.append("missing_motion")

        score = max(0, 100 - (len(issues) * 15))
        return {"score": score, "issues": issues}

    def decision(self, result: dict) -> str:
        issues = result.get("issues", [])
        score = int(result.get("score", 0))
        severe = {"too_short", "missing_environment", "missing_motion"}
        if score < 60 or any(issue in severe for issue in issues):
            return "REWRITE"
        if issues:
            return "FIX"
        return "KEEP"

    @staticmethod
    def _has_duplicate_lines(lines: list[str]) -> bool:
        seen: set[str] = set()
        for line in lines:
            key = line.lower()
            if key in seen:
                return True
            seen.add(key)
        return False

    def _has_character(self, segment: dict) -> bool:
        if not isinstance(segment, dict):
            return False
        visual_plan = segment.get("visual_plan", {})
        source = ""
        if isinstance(visual_plan, dict):
            source = str(visual_plan.get("subject", ""))
            details = visual_plan.get("details", [])
            if isinstance(details, list):
                source += " " + " ".join(str(item) for item in details)
        source += " " + str(segment.get("text", ""))
        lowered = source.lower()
        return bool(re.search(r"\b(person|man|woman|character|worker|face|hand)\b", lowered))
