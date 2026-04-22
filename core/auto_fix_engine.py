from __future__ import annotations

import random
import re


class AutoFixEngine:
    AI_WORDS = (
        "over time",
        "over 6 seconds",
        "then",
        "before",
        "while",
        "as if",
        "suggesting",
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
        (r"\bthe frame tightens\b", "the frame settles"),
        (r"\bcamera tracks\b", "the camera holds"),
        (r"\bfocus shifts intentionally\b", "attention remains"),
    )

    CAUSAL_PHRASES = (
        "because",
        "due to",
        "therefore",
        "so that",
        "in order to",
        "as a result",
    )
    LIGHT_VARIATIONS = (
        "light falls unevenly",
        "light spreads softly",
        "light breaks across surfaces",
    )
    ABSTRACT_WORDS = (
        "mood",
        "feeling",
        "emotion",
        "cinematic",
        "intention",
        "suggestive",
        "symbolic",
        "dramatic",
    )

    COMMON_VERBS = {
        "is",
        "are",
        "was",
        "were",
        "be",
        "holds",
        "hold",
        "moves",
        "move",
        "drifts",
        "drift",
        "settles",
        "settle",
        "appears",
        "appear",
        "remains",
        "remain",
        "shows",
        "show",
        "crosses",
        "cross",
        "falls",
        "fall",
        "shifts",
        "shift",
        "stays",
        "stay",
    }

    def fix(self, prompt: str, has_human: bool = False) -> str:
        text = str(prompt or "")
        text = self._replace_camera_phrases(text)
        text = self._remove_words(text, self.AI_WORDS)
        text = self._normalize_spacing(text)

        sentence_parts = self._split_sentences(text)
        filtered: list[str] = []
        for sentence in sentence_parts:
            cleaned = self._normalize_sentence(sentence)
            if not cleaned:
                continue
            cleaned = self._remove_causal_phrases(cleaned)
            cleaned = self._rewrite_abstract_sentence(cleaned)
            if not has_human:
                cleaned = self._replace_human_with_observational(cleaned)
            if len(cleaned.split()) < 4:
                cleaned = self._replace_short_sentence(cleaned)
            if not self._has_subject_and_verb(cleaned):
                cleaned = self._replace_invalid_sentence(cleaned)
            filtered.append(cleaned)

        deduped = self._dedupe_similar_sentences(filtered)
        deduped = self._dedupe_concepts(deduped)
        deduped = self._rephrase_one_sentence(deduped)
        deduped = self._ensure_required_components(deduped)
        deduped = self._ensure_minimum_sentences(deduped, minimum=5)
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

    def _has_subject_and_verb(self, sentence: str) -> bool:
        if sentence.lower().startswith("duration:"):
            return True
        words = [w.strip(" ,;.!?").lower() for w in sentence.split() if w.strip(" ,;.!?")]
        if len(words) < 4:
            return False
        has_subject = any(w in {"the", "a", "an", "this", "that", "it", "frame", "camera"} for w in words)
        has_verb = any(w in self.COMMON_VERBS or w.endswith("ing") or w.endswith("ed") for w in words)
        return has_subject and has_verb

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

    def _dedupe_concepts(self, sentences: list[str]) -> list[str]:
        kept: list[str] = []
        concept_seen: set[str] = set()
        concept_map = {
            "dust": ("dust", "particle", "particles"),
            "light": ("light", "flicker", "reflection"),
        }
        for sentence in sentences:
            lowered = sentence.lower()
            concepts_in_sentence = {
                concept
                for concept, markers in concept_map.items()
                if any(marker in lowered for marker in markers)
            }
            if concepts_in_sentence & concept_seen:
                continue
            concept_seen.update(concepts_in_sentence)
            kept.append(sentence)
        return kept

    def _remove_causal_phrases(self, sentence: str) -> str:
        output = sentence
        for phrase in self.CAUSAL_PHRASES:
            output = re.sub(rf"\b{re.escape(phrase)}\b", "", output, flags=re.IGNORECASE)
        output = " ".join(output.split()).strip(" ,;.")
        if output and output[-1] not in ".!?":
            output += "."
        return output

    def _rewrite_abstract_sentence(self, sentence: str) -> str:
        lowered = sentence.lower()
        if any(word in lowered for word in self.ABSTRACT_WORDS):
            return "Visible surfaces and object edges remain clear under uneven light."
        return sentence

    def _replace_human_with_observational(self, sentence: str) -> str:
        lowered = sentence.lower()
        if any(word in lowered for word in self.HUMAN_WORDS):
            return "Dust particles shift near the window and small object edges move slightly."
        return sentence

    @staticmethod
    def _replace_short_sentence(sentence: str) -> str:
        if sentence.lower().startswith("duration:"):
            return sentence
        return "Table, shelf, and paper details remain visible in the frame."

    @staticmethod
    def _replace_invalid_sentence(sentence: str) -> str:
        if sentence.lower().startswith("duration:"):
            return sentence
        return "Object positions remain clear and surface detail stays visible."

    def _rephrase_one_sentence(self, sentences: list[str]) -> list[str]:
        if not sentences:
            return sentences

        candidate_indices = [
            i for i, sentence in enumerate(sentences)
            if not sentence.lower().startswith("duration:")
        ]
        if not candidate_indices:
            return sentences

        light_indices = [
            i for i in candidate_indices
            if any(word in sentences[i].lower() for word in ("light", "shadow", "surface"))
        ]
        target_indices = light_indices or candidate_indices
        target = random.choice(target_indices)

        original = sentences[target].strip().rstrip(".!?")
        variation = random.choice(self.LIGHT_VARIATIONS)
        updated = f"{original}; {variation}."
        updated = self._normalize_spacing(updated)

        updated_sentences = list(sentences)
        updated_sentences[target] = updated
        return updated_sentences

    def _ensure_required_components(self, sentences: list[str]) -> list[str]:
        has_duration = any(s.lower().startswith("duration:") for s in sentences)
        has_environment = any(
            any(w in s.lower() for w in ("room", "space", "hallway", "street", "office", "factory"))
            for s in sentences
        )
        has_objects = any(
            any(w in s.lower() for w in ("desk", "paper", "table", "shelf", "chair", "window", "folder"))
            for s in sentences
        )
        has_light = any(any(w in s.lower() for w in ("light", "shadow", "reflection")) for s in sentences)
        has_motion = any(
            any(w in s.lower() for w in ("moves", "drift", "shifts", "settles", "flicker", "sways"))
            for s in sentences
        )

        output = list(sentences)
        if not has_environment:
            output.append("Office room space remains visible with clear depth from front to back.")
        if not has_objects:
            output.append("Wood desk, paper stack, and shelf labels are visible in frame.")
        if not has_light:
            output.append("Light falls unevenly across surfaces with softer shadow near the edges.")
        if not has_motion:
            output.append("A paper corner shifts slightly near the front edge of the desk.")
        if not has_duration:
            output.append("Duration: 6 seconds")
        return output

    @staticmethod
    def _ensure_minimum_sentences(sentences: list[str], minimum: int = 5) -> list[str]:
        fillers = (
            "Background wall texture remains visible with minor contrast variation.",
            "Object spacing stays clear across the middle section of the frame.",
            "Window light remains soft with gradual falloff near the side wall.",
        )
        output = list(sentences)
        idx = 0
        while len([s for s in output if not s.lower().startswith("duration:")]) < minimum:
            output.append(fillers[idx % len(fillers)])
            idx += 1
        return output

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
