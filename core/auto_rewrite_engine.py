from __future__ import annotations

import re


class AutoRewriteEngine:
    def rewrite(self, prompt: str, segment: dict) -> str:
        source = self._source_text(prompt, segment).lower()
        has_human = self._has_human(source)
        environment = self._environment_line(source)
        objects = self._object_line(source)
        light = self._light_line(source)
        motion = self._motion_line(source, has_human)
        camera = self._camera_line(segment)
        duration = "Duration: 6 seconds"

        lines = [
            environment,
            objects,
            light,
            motion,
            camera,
            duration,
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
        return "\n\n".join(deduped[:6])

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
            return "Street space with visible storefronts and pavement depth"
        if "factory" in source:
            return "Factory room with metal structure and open floor space"
        if "hallway" in source:
            return "Hallway space with clear wall lines and floor depth"
        return "Office room with clear foreground and background separation"

    @staticmethod
    def _object_line(source: str) -> str:
        if "factory" in source:
            return "Metal pipes, control panels, and tool cart are visible"
        if "street" in source:
            return "Road signs, parked vehicles, and curb markers are visible"
        return "Wood desk, paper stack, shelf labels, and wall clock are visible"

    @staticmethod
    def _light_line(source: str) -> str:
        if "night" in source:
            return "Low light remains uneven with darker edges and soft reflections"
        if "rain" in source:
            return "Diffuse daylight spreads through moisture and soft window reflection"
        return "Light falls unevenly across surfaces with soft edge shadow"

    @staticmethod
    def _motion_line(source: str, has_human: bool) -> str:
        if not has_human:
            if "dust" in source:
                return "Dust particles remain visible in the light beam"
            return "A paper corner shifts slightly near the desk edge"
        return "A small hand adjustment appears with restrained body movement"

    @staticmethod
    def _camera_line(segment: dict) -> str:
        camera = str(segment.get("camera", "")).strip().lower() if isinstance(segment, dict) else ""
        if camera == "wide":
            return "Wide frame holds with subtle drift and stable horizon"
        if camera == "close":
            return "Close frame holds on surface detail with minor drift"
        return "Medium frame settles with slight inward drift"

    @staticmethod
    def _sentence(value: str) -> str:
        text = " ".join(str(value).strip().split()).strip(" ,;.")
        text = re.sub(r"\b(as if|suggesting|therefore|because)\b", "", text, flags=re.IGNORECASE)
        text = " ".join(text.split()).strip(" ,;.")
        if not text:
            return ""
        if text.lower().startswith("duration:"):
            return text
        if text[-1] not in ".!?":
            text += "."
        return text
