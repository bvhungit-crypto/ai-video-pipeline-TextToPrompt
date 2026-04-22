from __future__ import annotations

import re


class AutoRewriteEngine:
    def rewrite(self, segment: dict, prompt: str = "") -> str:
        source = self._source_text(prompt, segment).lower()
        has_human = self._has_human(source)
        style = self._style_line(source)
        environment = self._environment_line(source)
        light = self._light_line(source)
        motion = self._motion_line(source, has_human)
        camera = self._camera_line(segment)

        # Strict cinematic order:
        # 1) style, 2) environment, 3) light, 4) subtle motion, 5) camera
        lines = [
            style,
            environment,
            light,
            motion,
            camera,
        ]
        cleaned = [self._sentence(line) for line in lines if line]
        deduped: list[str] = []
        seen: set[str] = set()
        for line in cleaned:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        # Keep natural flow and minimum 4 sentences.
        if len(deduped) < 4:
            deduped.append("The camera holds briefly on the same area.")
        return "\n\n".join(deduped[:5])

    @staticmethod
    def _style_line(source: str) -> str:
        if "animation" in source or "2d" in source:
            return "2D animation style, soft shading, simple camera movement."
        if "surveillance" in source:
            return "Surveillance style, fixed camera, low-resolution image."
        return "Documentary realism, handheld camera, natural light."

    @staticmethod
    def _source_text(prompt: str, segment: dict) -> str:
        seg_text = ""
        if isinstance(segment, dict):
            seg_text = str(segment.get("text", "")) + " " + str(segment.get("prompt", ""))
        return f"{prompt} {seg_text}".strip()

    @staticmethod
    def _has_human(source: str) -> bool:
        return any(w in source for w in ("she", "he", "person", "man", "woman", "character"))

    @staticmethod
    def _environment_line(source: str) -> str:
        if "street" in source:
            return "A city street extends past storefronts and wet pavement."
        if "factory" in source:
            return "A factory room opens across metal structure and concrete floor."
        if "hallway" in source:
            return "A hallway stretches forward with plain walls and floor marks."
        return "An office room holds a desk area near a window and rear wall."

    @staticmethod
    def _light_line(source: str) -> str:
        if "night" in source:
            return "Low light fades along the edges and leaves soft reflections on surfaces."
        if "rain" in source:
            return "Diffuse daylight spreads through moisture and soft window reflection."
        return "Light falls unevenly across the room and wraps softly over nearby objects."

    @staticmethod
    def _motion_line(source: str, has_human: bool) -> str:
        if not has_human:
            if "dust" in source:
                return "Dust particles drift slowly through the light beam."
            return "A paper corner shifts slightly near the edge of the desk."
        return "A small hand adjustment appears near the foreground object."

    @staticmethod
    def _camera_line(segment: dict) -> str:
        camera = str(segment.get("camera", "")).strip().lower() if isinstance(segment, dict) else ""
        if camera == "wide":
            return "The camera holds a wide view and drifts slightly inward."
        if camera == "close":
            return "The camera holds close on surface detail with a slight drift."
        return "The camera holds a medium view with gentle drift."

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
