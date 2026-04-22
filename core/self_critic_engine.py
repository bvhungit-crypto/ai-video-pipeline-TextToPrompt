from __future__ import annotations

import re


class SelfCriticEngine:
    ABSTRACT_WORDS = ("balance", "tension", "focus")
    CAMERA_INTENT_WORDS = ("track", "reduce", "tighten", "guide", "follow", "balance shift")
    HUMAN_WORDS = (
        "she",
        "he",
        "person",
        "man",
        "woman",
        "character",
        "hand",
        "hands",
        "jaw",
        "shoulder",
        "shoulders",
        "breath",
        "body",
        "face",
    )
    ENVIRONMENT_WORDS = ("room", "desk", "space")
    MOTION_WORDS = ("move", "shift", "drift", "lift")

    def evaluate(self, prompt: str, segment: dict, previous_prompt: str = "") -> dict:
        text = str(prompt or "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lower = text.lower()
        issues: list[str] = []
        score = 100

        if len(lines) < 5:
            issues.append("too_short")
            score -= 15

        if self._has_duplicate_lines(lines):
            issues.append("duplicate_lines")
            score -= 15

        if self._is_list_style(lines):
            issues.append("list_style")
            score -= 15

        if any(word in lower for word in self.ABSTRACT_WORDS):
            issues.append("abstract_words")
            score -= 15

        if any(word in lower for word in self.CAMERA_INTENT_WORDS):
            issues.append("camera_intent_words")
            score -= 15

        has_character = self._has_character(segment)
        if not has_character and any(word in lower for word in self.HUMAN_WORDS):
            issues.append("human_error")
            score -= 40

        if not any(word in lower for word in self.ENVIRONMENT_WORDS):
            issues.append("missing_environment")
            score -= 15

        if not any(word in lower for word in self.MOTION_WORDS):
            issues.append("missing_motion")
            score -= 15

        if previous_prompt and self._similarity(text, previous_prompt) > 0.70:
            issues.append("duplicate_scene")
            score -= 30

        score = max(0, score)
        return {"score": score, "issues": issues}

    def decision(self, result: dict) -> str:
        issues = result.get("issues", [])
        score = int(result.get("score", 0))
        if "human_error" in issues or "duplicate_scene" in issues:
            return "REWRITE"
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

    @staticmethod
    def _is_list_style(lines: list[str]) -> bool:
        short_count = sum(1 for line in lines if len(line.split()) <= 5 and not line.lower().startswith("duration:"))
        comma_heavy = sum(1 for line in lines if line.count(",") >= 3)
        return short_count >= 3 or comma_heavy >= 2

    @staticmethod
    def _similarity(left: str, right: str) -> float:
        left_tokens = SelfCriticEngine._token_set(left)
        right_tokens = SelfCriticEngine._token_set(right)
        if not left_tokens or not right_tokens:
            return 0.0
        inter = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        if union == 0:
            return 0.0
        return inter / union

    @staticmethod
    def _token_set(text: str) -> set[str]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        stop = {"the", "a", "an", "and", "of", "to", "in", "on", "with", "for", "at", "by", "is", "are"}
        return {t for t in tokens if t not in stop}

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
