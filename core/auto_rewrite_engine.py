from __future__ import annotations

import re


class AutoRewriteEngine:
    NON_HUMAN_BANNED = ("hand", "body", "face", "breath", "shoulder")

    def __init__(self) -> None:
        self._used_sentence_keys: set[str] = set()

    def rewrite(self, segment: dict, prompt: str = "") -> str:
        source = self._source_text(prompt, segment).lower()
        has_human = bool(segment.get("has_human", False)) if isinstance(segment, dict) else False
        base_index = self._segment_index(segment)
        max_rewrite = 2
        for attempt in range(max_rewrite):
            candidate = self._build_candidate(source, segment, has_human, base_index + attempt)
            if self._validate_candidate(candidate, has_human):
                return candidate
        return self._force_valid_prompt(source, segment, has_human, base_index + max_rewrite)

    def _build_candidate(self, source: str, segment: dict, has_human: bool, segment_index: int) -> str:
        scene_type = str(segment.get("scene_type", "")).strip().lower() if isinstance(segment, dict) else ""
        environment_type = str(segment.get("environment", "")).strip().lower() if isinstance(segment, dict) else ""
        objects = segment.get("objects", []) if isinstance(segment, dict) else []
        if not isinstance(objects, list):
            objects = []

        lines = [
            self._style_line(source, segment_index),
            self._environment_line(scene_type, environment_type, objects),
            self._light_line(source, segment_index),
            self._motion_line(has_human, scene_type, objects),
            self._camera_line(segment, segment_index),
        ]
        cleaned = [self._sentence(line) for line in lines if line]
        if not has_human:
            cleaned = [self._strip_non_human_words(line) for line in cleaned]
        cleaned = [line for line in cleaned if line]
        while len(cleaned) < 5:
            cleaned.append(self._sentence(self._fallback_line(len(cleaned), segment_index)))
        return "\n\n".join(cleaned[:5])

    def _validate_candidate(self, prompt: str, has_human: bool) -> bool:
        lines = [line.strip() for line in str(prompt).splitlines() if line.strip()]
        if len(lines) < 5:
            return False
        light_line = lines[2].lower()
        motion_line = lines[3].lower()
        camera_line = lines[4].lower()
        if "light" not in light_line:
            return False
        if not any(w in motion_line for w in ("shift", "drift", "move", "motion")):
            return False
        if "camera" not in camera_line:
            return False
        if not has_human and any(w in prompt.lower() for w in self.NON_HUMAN_BANNED):
            return False
        return True

    def _force_valid_prompt(self, source: str, segment: dict, has_human: bool, segment_index: int) -> str:
        return self._build_candidate(source, segment, has_human, segment_index)

    @staticmethod
    def _style_line(source: str, segment_index: int) -> str:
        if "animation" in source or "2d" in source:
            variants = (
                "2D animation style with soft shading and restrained camera movement.",
                "2D animation style with clean shading and stable camera perspective.",
            )
            return variants[segment_index % len(variants)]
        return "Documentary realism with grounded camera behavior and natural light."

    @staticmethod
    def _source_text(prompt: str, segment: dict) -> str:
        seg_text = ""
        if isinstance(segment, dict):
            seg_text = str(segment.get("text", "")) + " " + str(segment.get("prompt", ""))
        return f"{prompt} {seg_text}".strip()

    @staticmethod
    def _environment_line(scene_type: str, environment_type: str, objects: list[str]) -> str:
        safe_objects = [str(obj).strip().lower() for obj in objects if str(obj).strip()]
        object_text = ", ".join(safe_objects[:3])
        if scene_type == "office":
            return (
                f"An office interior shows {object_text} across the workspace."
                if safe_objects
                else "An office interior is visible, with objects not provided in segment data."
            )
        if scene_type == "street":
            return (
                f"A street scene shows {object_text} along the road."
                if safe_objects
                else "A street scene is visible, with objects not provided in segment data."
            )
        if scene_type == "indoor":
            return (
                f"An indoor space shows {object_text} in the frame."
                if safe_objects
                else "An indoor space is visible, with objects not provided in segment data."
            )
        if scene_type == "outdoor":
            return (
                f"An outdoor area shows {object_text} in the frame."
                if safe_objects
                else "An outdoor area is visible, with objects not provided in segment data."
            )
        if environment_type == "interior":
            return (
                f"An interior scene shows {object_text} in view."
                if safe_objects
                else "An interior scene is visible, with objects not provided in segment data."
            )
        if environment_type == "exterior":
            return (
                f"An exterior scene shows {object_text} in view."
                if safe_objects
                else "An exterior scene is visible, with objects not provided in segment data."
            )
        return (
            f"The frame shows {object_text} from segment data."
            if safe_objects
            else "The frame is visible based on segment data."
        )

    @staticmethod
    def _light_line(source: str, segment_index: int) -> str:
        if "night" in source:
            return "Low light falls unevenly across surfaces and leaves dim edges."
        return "Light falls unevenly across surfaces and fades in background areas."

    @staticmethod
    def _motion_line(has_human: bool, scene_type: str, objects: list[str]) -> str:
        safe_objects = [str(obj).strip().lower() for obj in objects if str(obj).strip()]
        object_focus = safe_objects[0] if safe_objects else ""
        if not has_human:
            if scene_type == "office":
                if object_focus:
                    return f"The {object_focus} shifts slightly with minor air movement in the office."
                return "Subtle motion is visible in the office frame."
            if object_focus:
                return f"The {object_focus} moves slightly within the visible frame."
            return "Subtle motion is visible in the frame."
        if object_focus:
            return f"A hand near the {object_focus} makes a small positional adjustment."
        return "A hand makes a small positional adjustment."

    @staticmethod
    def _camera_line(segment: dict, segment_index: int) -> str:
        camera = str(segment.get("camera", "")).strip().lower() if isinstance(segment, dict) else ""
        if camera == "wide":
            return "The camera holds a wide view with slight drift."
        if camera == "close":
            return "The camera holds a close view with slight drift."
        return "The camera holds a medium view with slight drift."

    @staticmethod
    def _segment_index(segment: dict) -> int:
        if not isinstance(segment, dict):
            return 0
        try:
            return max(0, int(float(segment.get("start", 0.0)) // 6))
        except Exception:
            return 0

    @staticmethod
    def _fallback_line(position: int, _segment_index: int) -> str:
        fallback_by_position = {
            0: "Documentary realism with grounded camera behavior and natural light.",
            1: "An interior scene is visible based on segment data.",
            2: "Light falls unevenly across surfaces and fades in background areas.",
            3: "Subtle motion is visible within the frame.",
            4: "The camera holds a medium view with slight drift.",
        }
        return fallback_by_position.get(position, fallback_by_position[4])

    def _strip_non_human_words(self, sentence: str) -> str:
        text = sentence
        for word in self.NON_HUMAN_BANNED:
            text = re.sub(rf"\b{re.escape(word)}s?\b", "", text, flags=re.IGNORECASE)
        text = " ".join(text.split()).strip(" ,;.")
        if not text:
            return ""
        if text[-1] not in ".!?":
            text += "."
        return text

    @staticmethod
    def _sentence(value: str) -> str:
        text = " ".join(str(value).strip().split()).strip(" ,;.")
        text = re.sub(r"\b(as if|suggesting|therefore|because|balance|tension|emotion)\b", "", text, flags=re.IGNORECASE)
        text = " ".join(text.split()).strip(" ,;.")
        if not text:
            return ""
        if text[-1] not in ".!?":
            text += "."
        return text
