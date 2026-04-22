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
        details = self._details_line(details_items)
        environment = self._clean_sentence(visual_plan.get("environment", "Neutral indoor light"))
        camera_value = str(segment.get("camera", "medium")).strip().lower()
        motion = self._clean_sentence(visual_plan.get("motion", "minor background movement"))
        segment_index = max(0, int(float(segment.get("start", 0.0)) // 6))
        human_subject = self._has_human_subject(subject, details_items)

        physical_action = self.build_physical_action(subject, motion, camera_value, segment_index, human_subject)
        light_behavior = self.build_light_behavior(environment, details, segment_index)
        body_tension = self.build_body_tension_layer(motion, details, segment_index, human_subject)
        camera_intent = self.build_camera_intent(camera_value, segment_index)
        frame_evolution = self.build_frame_evolution(camera_value, segment_index)

        shot_safe_motion = self._motion_for_shot(
            camera=camera_value,
            motion=motion,
            details=details_items,
            environment=environment,
        )

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
                f"{base_subject}; foreground objects settle before fine particles shift",
                f"{base_subject}; object positions hold while small surface elements move",
                f"{base_subject}; frame starts stable, then a slight object shift appears",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                f"{base_subject}; weight shifts first, then the hand follows with slight delay",
                f"{base_subject}; wrist adjusts first, then finger position follows a moment later",
                f"{base_subject}; posture holds, then a small hand correction lands at the end",
            )
            return variants[segment_index % len(variants)]
        if camera == "wide":
            variants = (
                f"{base_subject}; weight shifts first, then the body follows with slight delay",
                f"{base_subject}; stance changes in two steps, feet first and shoulders second",
                f"{base_subject}; body weight transfers gradually before the frame settles",
            )
            return variants[segment_index % len(variants)]
        variants = (
            f"{base_subject}; weight transfers through the feet before the torso follows",
            f"{base_subject}; center of weight moves first, then shoulders align",
            f"{base_subject}; posture adjusts in sequence, lower body then upper body",
        )
        return variants[segment_index % len(variants)]

    def build_light_behavior(self, environment: str, details: str, segment_index: int) -> str:
        env = environment.rstrip(".")
        variants = (
            f"{env}; uneven light wraps across surfaces with falloff at the frame edges",
            f"{env}; light stays irregular, with dim zones behind foreground objects",
            f"{env}; soft wrap remains on primary objects while side areas stay darker",
        )
        return variants[segment_index % len(variants)]

    def build_body_tension_layer(self, motion: str, details: str, segment_index: int, human_subject: bool) -> str:
        if not human_subject:
            variants = (
                "Dust particles remain visible near the window line",
                "Light changes slightly across object edges and surface texture",
                "Small object shifts are visible along the table surface",
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
                "Wide framing holds full spatial context and then tightens slightly",
                "Wide framing keeps room geometry clear before a subtle inward shift",
                "Wide framing observes the full scene and reduces distance gradually",
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
                "Over 6 seconds the frame tightens slightly and center balance shifts inward",
                "Over 6 seconds the frame drifts forward and depth compresses softly",
                "Over 6 seconds framing narrows a little and object spacing becomes denser",
            )
            return variants[segment_index % len(variants)]
        if camera == "close":
            variants = (
                "Over 6 seconds the frame compresses slightly and micro-shifts settle",
                "Over 6 seconds focus tightens and edge movement slows",
                "Over 6 seconds framing remains tight while detail balance shifts slightly",
            )
            return variants[segment_index % len(variants)]
        variants = (
            "Over 6 seconds the frame moves forward slightly and settles toward center",
            "Over 6 seconds the frame compresses gently and maintains object balance",
            "Over 6 seconds the frame drifts inward and then stabilizes",
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
        if not text:
            return ""
        if text.lower().startswith("duration:"):
            return text
        if text[-1] not in ".!?":
            text += "."
        return text

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
