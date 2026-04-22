from __future__ import annotations

from typing import Any

from core.style_presets import STYLE_PRESETS


class PromptEngine:
    def __init__(self, style: str = "cinematic_dark", mode: str = "character") -> None:
        style_key = str(style).strip().lower() or "cinematic_dark"
        self.style_line = STYLE_PRESETS.get(style_key, STYLE_PRESETS["cinematic_dark"])
        self.mode = mode

    def build(self, segment: dict[str, Any]) -> str:
        visual_plan = segment.get("visual_plan", {})
        subject = self._clean_sentence(visual_plan.get("subject", "Office room with wooden desk and paper stacks"))
        details_items = visual_plan.get("details", [])
        segment_objects = segment.get("objects", [])
        if isinstance(segment_objects, list) and segment_objects:
            details_items = segment_objects
        details = self._details_line(details_items)
        environment = self._clean_sentence(visual_plan.get("environment", "Neutral indoor light"))
        camera_value = str(segment.get("camera", "medium")).strip().lower()
        motion = self._clean_sentence(visual_plan.get("motion", "minor background movement"))
        segment_index = max(0, int(float(segment.get("start", 0.0)) // 6))
        human_subject = bool(segment.get("has_human", self._has_human_subject(subject, details_items)))

        physical_action = self.build_physical_action(subject, motion, camera_value, segment_index, human_subject)
        light_behavior = self.build_light_behavior(environment, details, segment_index)
        shot_safe_motion = self._motion_for_shot(
            camera=camera_value,
            motion=motion,
            details=details_items,
            environment=environment,
        )
        body_tension = self.build_body_tension_layer(
            motion,
            details,
            segment_index,
            human_subject,
            shot_safe_motion,
        )
        camera_intent = self.build_camera_intent(camera_value, segment_index)
        frame_evolution = self.build_frame_evolution(camera_value, segment_index)

        lines = [
            self._clean_sentence(self.style_line),
            self._clean_sentence(physical_action),
            self._clean_sentence(light_behavior),
            self._clean_sentence(body_tension),
            self._clean_sentence(camera_intent),
            self._clean_sentence(frame_evolution),
            details,
            self._clean_sentence(shot_safe_motion),
            "Duration: 6 seconds",
        ]
        deduped: list[str] = []
        seen: set[str] = set()
        for line in lines:
            key = line.lower()
            if not line or key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        return "\n\n".join(deduped)

    def build_physical_action(
        self,
        subject: str,
        motion: str,
        camera: str,
        segment_index: int,
        human_subject: bool,
    ) -> str:
        base_subject = subject.rstrip(".")
        if not human_subject:
            variants = (
                f"{base_subject}; foreground objects remain stable, fine particles shift near surfaces",
                f"{base_subject}; object positions remain fixed, small surface elements move",
                f"{base_subject}; frame stays stable, a slight object shift appears near the edge",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                f"{base_subject}; weight shift appears first, hand movement follows with slight delay",
                f"{base_subject}; wrist adjustment appears first, finger position changes a moment later",
                f"{base_subject}; posture remains steady, a small hand correction appears at the end",
            )
            return variants[segment_index % len(variants)]
        if camera == "wide":
            variants = (
                f"{base_subject}; weight shift appears first, body movement follows with slight delay",
                f"{base_subject}; stance changes in two stages, feet first, shoulders second",
                f"{base_subject}; body weight transfers gradually, frame settles at the end",
            )
            return variants[segment_index % len(variants)]
        variants = (
            f"{base_subject}; weight transfers through the feet, torso follows after a short delay",
            f"{base_subject}; center of weight changes first, shoulders align after the shift",
            f"{base_subject}; posture adjusts in sequence, lower body first, upper body second",
        )
        return variants[segment_index % len(variants)]

    def build_light_behavior(self, environment: str, details: str, segment_index: int) -> str:
        env = environment.rstrip(".")
        variants = (
            f"{env}; uneven light wraps across surfaces with falloff at the frame edges",
            f"{env}; light stays irregular, with dim zones behind foreground objects",
            f"{env}; soft wrap remains on primary objects, side areas stay darker",
        )
        return variants[segment_index % len(variants)]

    def build_body_tension_layer(
        self,
        motion: str,
        details: str,
        segment_index: int,
        human_subject: bool,
        shot_safe_motion: str,
    ) -> str:
        if not human_subject:
            shot_motion = shot_safe_motion.lower()
            if "dust" in shot_motion:
                variants = (
                    "Light intensity changes slightly across object edges",
                    "Small object shifts remain visible on the table line",
                    "Surface reflections change slightly across metal and paper",
                )
            elif "light" in shot_motion or "reflection" in shot_motion:
                variants = (
                    "Dust remains visible near the window line",
                    "Small object shifts remain visible near the table edge",
                    "Surface particles settle on paper and metal surfaces",
                )
            else:
                variants = (
                    "Dust remains visible near the window line",
                    "Light changes slightly across object edges",
                    "Small object shifts remain visible on the table surface",
                )
            return variants[segment_index % len(variants)]
        variants = (
            "Breath stays shallow, shoulders hold slight tension, and hands remain controlled",
            "Shoulders stay braced, jaw line stays set, and breath remains short",
            "Hands stay steady, shoulder tension remains visible, and breath is restrained",
        )
        return variants[segment_index % len(variants)]

    def build_camera_intent(self, camera: str, segment_index: int) -> str:
        if camera == "wide":
            variants = (
                "Wide framing holds full spatial context and drifts slightly inward",
                "Wide framing keeps room geometry clear with a subtle inward drift",
                "Wide framing keeps the full scene in view with gradual distance change",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                "Close framing stays on surface detail with steady distance control",
                "Close framing remains tight on texture and edge movement",
                "Close framing keeps detail priority with minimal reframing",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "Medium framing closes distance slowly with stable alignment",
            "Medium framing tracks object relation while reducing space gradually",
            "Medium framing advances slightly and maintains balanced composition",
        )
        return variants[segment_index % len(variants)]

    def build_frame_evolution(self, camera: str, segment_index: int) -> str:
        if camera == "wide":
            variants = (
                "Frame balance shifts inward with a subtle drift",
                "Frame drifts forward and depth compresses softly",
                "Framing narrows slightly and object spacing becomes denser",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                "Frame compresses slightly and micro-shifts settle",
                "Edge movement slows across surface detail",
                "Framing remains tight and detail balance shifts slightly",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "Frame moves forward slightly and settles near center",
            "Frame compresses gently and maintains object balance",
            "Frame drifts inward and stabilizes",
        )
        return variants[segment_index % len(variants)]

    @staticmethod
    def _details_line(details: Any) -> str:
        if isinstance(details, list):
            parts = [str(item).strip() for item in details if str(item).strip()]
            if parts:
                unique_parts: list[str] = []
                seen: set[str] = set()
                for part in parts:
                    key = part.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    unique_parts.append(part)
                return PromptEngine._clean_sentence(", ".join(unique_parts))
        return "Wood desk surface, paper stack, and wall clock"

    @staticmethod
    def _motion_for_shot(camera: Any, motion: Any, details: Any, environment: Any) -> str:
        camera_value = str(camera).strip().lower()
        motion_text = " ".join(str(motion).strip().split()).lower()
        env_text = " ".join(str(environment).strip().split()).lower()
        detail_text = " ".join(str(item).strip().lower() for item in details) if isinstance(details, list) else ""

        if camera_value == "wide":
            if "rain" in env_text:
                return "Rain falls lightly across the window area."
            if "dust" in motion_text or "dust" in env_text:
                return "Dust particles are visible in the light beam."
            if "air" in motion_text or "curtain" in detail_text:
                return "Curtain moves slightly near the window."
            return "Light air movement is visible in the room."

        if camera_value == "close":
            if "paper" in detail_text:
                return "Paper edge lifts slightly."
            if "clip" in detail_text or "metal" in detail_text:
                return "Dust settles on the metal surface."
            if "ink" in detail_text:
                return "Paper corner shifts slightly."
            return "Small surface particles shift slightly."

        # Medium shot: motion must relate to objects in frame.
        if "paper" in detail_text or "folder" in detail_text:
            return "Top folder page moves slightly."
        if "screen" in detail_text or "monitor" in detail_text:
            return "Monitor reflection changes with minor camera movement."
        if "cable" in detail_text:
            return "Loose cable moves slightly near the desk edge."
        return "Small object movement is visible on the table."

    @staticmethod
    def _clean_sentence(value: Any) -> str:
        text = " ".join(str(value).strip().split()).strip(" ,;.")
        text = PromptEngine._strip_explanatory_phrases(text)
        if not text:
            return ""
        if text.lower().startswith("duration:"):
            return text
        if text[-1] not in ".!?":
            text += "."
        return text

    @staticmethod
    def _strip_explanatory_phrases(text: str) -> str:
        replacements = {
            " as if ": " ",
            " suggesting ": " ",
            " while ": ", ",
        }
        normalized = f" {text} "
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        normalized = " ".join(normalized.split())
        normalized = normalized.replace(" ,", ",").strip(" ,;.")
        return normalized

    @staticmethod
    def _has_human_subject(subject: str, details: Any) -> bool:
        source = str(subject).lower()
        if isinstance(details, list):
            source += " " + " ".join(str(item).lower() for item in details)
        human_words = (
            "person",
            "people",
            "woman",
            "man",
            "character",
            "face",
            "hand",
            "human",
            "worker",
            "body",
        )
        return any(word in source for word in human_words)
