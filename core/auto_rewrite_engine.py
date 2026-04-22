from __future__ import annotations

import re


class AutoRewriteEngine:
    def rewrite(self, segment: dict, prompt: str = "") -> str:
        source = self._source_text(prompt, segment).lower()
        has_human = self._has_human(source)
        segment_index = self._segment_index(segment)
        style = self._style_line(source, segment_index)
        environment = self._environment_line(source, segment_index)
        light = self._light_line(source, segment_index)
        motion = self._motion_line(source, has_human, segment_index)
        camera = self._camera_line(segment, segment_index)

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
        while len(deduped) < 5:
            deduped.append(self._fallback_line(len(deduped), segment_index))
        return "\n\n".join(deduped[:5])

    @staticmethod
    def _style_line(source: str, segment_index: int) -> str:
        if "animation" in source or "2d" in source:
            variants = (
                "2D animation style with soft shading and restrained camera movement.",
                "2D animation style with clean shading and stable camera perspective.",
                "2D animation style with soft tonal rendering and simple camera movement.",
            )
            return variants[segment_index % len(variants)]
        if "surveillance" in source:
            variants = (
                "Surveillance style with fixed camera framing and low-resolution image quality.",
                "Surveillance style with static camera angle and compressed visual texture.",
                "Surveillance style with fixed perspective and low-detail image structure.",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "Documentary realism with handheld camera behavior and natural light response.",
            "Documentary realism with grounded handheld framing and natural light behavior.",
            "Documentary realism with stable handheld perspective and natural light falloff.",
        )
        return variants[segment_index % len(variants)]

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
    def _environment_line(source: str, segment_index: int) -> str:
        if "street" in source:
            variants = (
                "A city street extends past closed storefronts and damp pavement.",
                "A street corridor remains open with curb lines and roadside signage.",
                "A street block continues through storefront fronts and marked pavement edges.",
            )
            return variants[segment_index % len(variants)]
        if "factory" in source:
            variants = (
                "A factory room opens across metal structure and worn concrete floor.",
                "An industrial room extends through steel framing and marked floor lanes.",
                "A production room remains visible with beam structure and open floor area.",
            )
            return variants[segment_index % len(variants)]
        if "hallway" in source:
            variants = (
                "A hallway stretches forward with plain walls and visible floor marks.",
                "A hallway section remains open with wall texture and corridor depth.",
                "A hallway space extends through flat walls and worn floor paths.",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "An office room holds a desk area near the window and back wall.",
            "An office interior extends from the desk area to the far wall.",
            "An office space remains open with desk surfaces and rear shelving.",
        )
        return variants[segment_index % len(variants)]

    @staticmethod
    def _light_line(source: str, segment_index: int) -> str:
        if "night" in source:
            variants = (
                "Low light fades along the edges and leaves soft reflections on surfaces.",
                "Night light remains uneven with dim corners and mild surface reflection.",
                "Low nighttime light drops at frame edges and softens object contours.",
            )
            return variants[segment_index % len(variants)]
        if "rain" in source:
            variants = (
                "Diffuse daylight spreads through moisture and soft window reflection.",
                "Rain-filtered daylight remains soft and fades across reflective surfaces.",
                "Moist air diffuses daylight and lowers contrast around object edges.",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "Light falls unevenly across the room and wraps softly over nearby objects.",
            "Natural light drops gradually toward the edges and softens object contours.",
            "Window light remains irregular across surfaces and fades in background areas.",
        )
        return variants[segment_index % len(variants)]

    @staticmethod
    def _motion_line(source: str, has_human: bool, segment_index: int) -> str:
        if not has_human:
            if "dust" in source:
                variants = (
                    "Dust particles drift slowly through the visible light beam.",
                    "Fine dust moves gradually across the lit section of the frame.",
                    "Dust remains visible as it shifts through the light path.",
                )
                return variants[segment_index % len(variants)]
            variants = (
                "A paper corner shifts slightly near the edge of the desk.",
                "A loose page edge moves slightly above the desk surface.",
                "A thin sheet corner lifts slightly and settles near the front edge.",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "A small hand adjustment appears near the foreground object.",
            "A brief hand movement appears beside the nearest surface.",
            "A restrained hand motion appears near the front of the frame.",
        )
        return variants[segment_index % len(variants)]

    @staticmethod
    def _camera_line(segment: dict, segment_index: int) -> str:
        camera = str(segment.get("camera", "")).strip().lower() if isinstance(segment, dict) else ""
        if camera == "wide":
            variants = (
                "The camera holds a wide view and drifts slightly inward.",
                "The camera keeps wide framing and settles with minor drift.",
                "The camera maintains wide framing with subtle positional drift.",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                "The camera holds close on surface detail with a slight drift.",
                "The camera keeps close framing and settles with minor drift.",
                "The camera remains close to texture detail with gentle drift.",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "The camera holds a medium view with gentle drift.",
            "The camera keeps medium framing and settles with slight drift.",
            "The camera maintains medium distance with subtle frame drift.",
        )
        return variants[segment_index % len(variants)]

    @staticmethod
    def _segment_index(segment: dict) -> int:
        if not isinstance(segment, dict):
            return 0
        try:
            return max(0, int(float(segment.get("start", 0.0)) // 6))
        except Exception:
            return 0

    @staticmethod
    def _fallback_line(position: int, segment_index: int) -> str:
        fallback_by_position = {
            0: (
                "Documentary realism with handheld camera behavior and natural light response.",
                "Documentary realism with grounded handheld framing and natural light behavior.",
            ),
            1: (
                "An office room holds a desk area near the window and back wall.",
                "An office interior extends from the desk area to the far wall.",
            ),
            2: (
                "Light falls unevenly across the room and wraps softly over nearby objects.",
                "Window light remains irregular across surfaces and fades in background areas.",
            ),
            3: (
                "A paper corner shifts slightly near the edge of the desk.",
                "A loose page edge moves slightly above the desk surface.",
            ),
            4: (
                "The camera holds a medium view with gentle drift.",
                "The camera keeps medium framing and settles with slight drift.",
            ),
        }
        variants = fallback_by_position.get(position, fallback_by_position[4])
        return variants[segment_index % len(variants)]

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
