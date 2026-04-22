from __future__ import annotations

import re


class AutoFixEngine:
    AI_WORDS = (
        "over time",
        "over 6 seconds",
        "then",
        "before",
    )

    HUMAN_WORDS = (
        "breath",
        "shoulder",
        "posture",
        "hand",
        "hands",
        "jaw",
    )

    CAMERA_REPLACEMENTS = (
        (r"\bslow push-?in\b", "a slight inward drift"),
        (r"\btightens\b", "settles slightly closer"),
        (r"\bfocuses\b", "holds attention"),
    )

    def fix(self, prompt: str, has_human: bool = False) -> str:
        text = str(prompt or "")
        text = self._replace_camera_phrases(text)
        text = self._remove_words(text, self.AI_WORDS)
        if not has_human:
            text = self._remove_words(text, self.HUMAN_WORDS)
        text = self._normalize_spacing(text)

        sentence_parts = [self._normalize_sentence(s) for s in self._split_sentences(text)]
        sentence_parts = [s for s in sentence_parts if s]
        deduped = self._dedupe_similar_sentences(sentence_parts)
        joined = "\n\n".join(deduped)
        joined = self._dedupe_lines(joined)
        return self._normalize_spacing(joined)

    def _replace_camera_phrases(self, text: str) -> str:
        output = text
        for pattern, replacement in self.CAMERA_REPLACEMENTS:
            output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
        return output

    @staticmethod
    def _remove_words(text: str, words: tuple[str, ...]) -> str:
        output = text
        for word in words:
            output = re.sub(rf"\b{re.escape(word)}\b", "", output, flags=re.IGNORECASE)
        return output

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        chunks: list[str] = []
        for line in lines:
            pieces = re.split(r"(?<=[.!?])\s+", line)
            for piece in pieces:
                part = piece.strip()
                if part:
                    chunks.append(part)
        return chunks

    @staticmethod
    def _normalize_sentence(sentence: str) -> str:
        cleaned = " ".join(sentence.strip().split()).strip(" ,;.")
        if not cleaned:
            return ""
        if cleaned.lower().startswith("duration:"):
            return cleaned
        if cleaned[-1] not in ".!?":
            cleaned += "."
        return cleaned

    def _dedupe_similar_sentences(self, sentences: list[str]) -> list[str]:
        kept: list[str] = []
        signatures: list[set[str]] = []
        for sentence in sentences:
            sig = self._signature(sentence)
            if not sig:
                continue
            if any(self._jaccard(sig, existing) >= 0.75 for existing in signatures):
                continue
            signatures.append(sig)
            kept.append(sentence)
        return kept

    @staticmethod
    def _signature(sentence: str) -> set[str]:
        words = [
            w.strip(" ,;.!?").lower()
            for w in sentence.split()
            if w.strip(" ,;.!?")
        ]
        stop = {"the", "a", "an", "and", "of", "to", "in", "on", "with", "for", "at", "by", "is", "are"}
        return {w for w in words if w not in stop}

    @staticmethod
    def _jaccard(left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        inter = len(left & right)
        union = len(left | right)
        if union == 0:
            return 0.0
        return inter / union

    @staticmethod
    def _dedupe_lines(text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        deduped: list[str] = []
        seen: set[str] = set()
        for line in lines:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        return "\n\n".join(deduped)

    @staticmethod
    def _normalize_spacing(text: str) -> str:
        normalized = re.sub(r"[ \t]+", " ", text)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = normalized.replace(" ,", ",").replace(" .", ".")
        return normalized.strip()
