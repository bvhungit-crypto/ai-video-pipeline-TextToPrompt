from __future__ import annotations

import re


class CleanEngine:
    TIMELINE_PHRASES = (
        "over time",
        "over 6 seconds",
        "within 6 seconds",
    )

    LOGIC_WORDS = tuple()
    EXPLANATORY_PHRASES = (
        "as if",
        "suggesting",
    )

    HUMAN_WORDS = (
        "breath",
        "shoulders",
        "jaw",
        "wrist",
        "fingers",
        "hands",
        "torso",
        "body",
    )

    def clean(self, prompt: str, has_character: bool) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        cleaned_lines: list[str] = []

        for line in lines:
            lower = line.lower()
            if lower.startswith("duration:"):
                cleaned_lines.append(line)
                continue

            line = self._remove_phrases(line, self.TIMELINE_PHRASES)
            line = self._remove_phrases(line, self.LOGIC_WORDS)
            line = self._remove_phrases(line, self.EXPLANATORY_PHRASES)
            line = line.replace(" while ", ", ")
            if not has_character:
                line = self._remove_phrases(line, self.HUMAN_WORDS)

            line = " ".join(line.split()).strip(" ,;.")
            if not line:
                continue
            if line[-1] not in ".!?":
                line += "."
            cleaned_lines.append(line)

        deduped: list[str] = []
        seen: set[str] = set()
        for line in cleaned_lines:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        return "\n\n".join(deduped)

    @staticmethod
    def _remove_phrases(text: str, phrases: tuple[str, ...]) -> str:
        output = text
        for phrase in phrases:
            output = re.sub(rf"\b{re.escape(phrase)}\b", "", output, flags=re.IGNORECASE)
        return output
