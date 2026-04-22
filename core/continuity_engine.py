from __future__ import annotations

from typing import Any


class ContinuityEngine:
    CAMERA_PROGRESSION = ("wide", "medium", "close")
    MOTION_FALLBACKS = (
        "she makes a subtle shift in weight",
        "the posture tightens slightly as motion continues",
        "the movement resolves into a controlled hold",
    )
    SEGMENT_DURATION_HINT = 6.0
    MOTION_PROGRESSIONS: dict[str, tuple[str, ...]] = {
        "stillness": (
            "she holds mostly still with a subtle shift in weight",
            "the posture tightens slightly while she remains nearly still",
            "her stillness turns into a controlled, intentional hold",
        ),
        "forward": (
            "she continues moving forward in one uninterrupted action",
            "her forward motion slows slightly as the posture tightens",
            "the forward movement resolves into a controlled near-stop",
        ),
        "gaze": (
            "her gaze continues on the same line with a slight adjustment",
            "her gaze narrows and settles with increased intention",
            "her gaze holds with quiet tension before release",
        ),
        "turn": (
            "she continues the turn with a small additional rotation",
            "the turn slows as shoulders tighten and align",
            "the turn resolves into a stable, intentional facing",
        ),
        "lift": (
            "the lifted motion continues a little higher",
            "the raised position firms as the movement slows",
            "the lift settles into a precise held position",
        ),
        "fallback": MOTION_FALLBACKS,
    }

    def apply(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        continuity_segments: list[dict[str, Any]] = []
        character_identity = self._build_character_identity(segments)
        environment = self._build_environment(segments)
        previous_motion = "continuous cinematic movement begins"
        previous_camera = self.CAMERA_PROGRESSION[0]

        for index, segment in enumerate(segments):
            camera_shot = self._next_camera_shot(
                index=index,
                previous_camera=previous_camera,
                segment=segment,
            )
            motion = self._build_motion(
                segment=segment,
                previous_motion=previous_motion,
                index=index,
            )
            emotional_state = self._build_emotional_state(
                segment=segment,
                index=index,
            )
            state = {
                "scene_reset": False,
                "camera": {
                    "shot": camera_shot,
                    "progression": f"{previous_camera} -> {camera_shot}",
                },
                "character_identity": character_identity,
                "environment": environment,
                "motion": motion,
                "emotional_state": emotional_state,
            }

            continuity_segments.append(
                {
                    **segment,
                    "state": state,
                    "previous_motion_reference": previous_motion,
                    "emotional_state": emotional_state,
                }
            )
            previous_motion = motion
            previous_camera = camera_shot

        return continuity_segments

    def _next_camera_shot(
        self,
        index: int,
        previous_camera: str,
        segment: dict[str, Any],
    ) -> str:
        if index == 0:
            return self.CAMERA_PROGRESSION[0]

        if previous_camera == self.CAMERA_PROGRESSION[-1]:
            return previous_camera

        density = int(segment.get("density", 0))
        duration_covered = float(segment.get("duration_covered", 0.0))

        should_hold = density <= 1 or duration_covered < (self.SEGMENT_DURATION_HINT / 2)
        if should_hold:
            return previous_camera

        current_position = self.CAMERA_PROGRESSION.index(previous_camera)
        next_position = min(current_position + 1, len(self.CAMERA_PROGRESSION) - 1)
        return self.CAMERA_PROGRESSION[next_position]

    @staticmethod
    def _build_character_identity(segments: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "fixed": True,
            "description": "a consistent cinematic protagonist with a clear visual presence",
        }

    @staticmethod
    def _build_environment(segments: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "fixed": True,
            "description": "a unified cinematic setting with stable lighting, atmosphere, and spatial continuity",
        }

    @classmethod
    def _build_motion(
        cls,
        segment: dict[str, Any],
        previous_motion: str,
        index: int,
    ) -> str:
        items = segment.get("items", [])
        if not items:
            return cls._fallback_motion(index=index, previous_motion=previous_motion)

        latest_text = str(items[-1].get("text", "")).strip().lower()
        if not latest_text:
            return cls._fallback_motion(index=index, previous_motion=previous_motion)

        category = cls._motion_category(latest_text)
        return cls._next_motion_step(
            category=category,
            previous_motion=previous_motion,
            index=index,
        )

    @classmethod
    def _fallback_motion(cls, index: int, previous_motion: str) -> str:
        return cls._next_motion_step(
            category="fallback",
            previous_motion=previous_motion,
            index=index,
        )

    @staticmethod
    def _motion_category(text: str) -> str:
        if any(word in text for word in ("stop", "pause", "still", "wait", "stand")):
            return "stillness"
        if any(word in text for word in ("look", "gaze", "glance", "stare")):
            return "gaze"
        if any(word in text for word in ("walk", "step", "move", "run", "approach", "forward")):
            return "forward"
        if any(word in text for word in ("turn", "pivot", "rotate")):
            return "turn"
        if any(word in text for word in ("reach", "raise", "lift", "extend")):
            return "lift"
        return "fallback"

    @classmethod
    def _next_motion_step(
        cls,
        category: str,
        previous_motion: str,
        index: int,
    ) -> str:
        progression = cls.MOTION_PROGRESSIONS.get(category, cls.MOTION_FALLBACKS)
        if not progression:
            return "the movement continues with subtle progression"

        if previous_motion in progression:
            previous_index = progression.index(previous_motion)
            next_index = min(previous_index + 1, len(progression) - 1)
            return progression[next_index]

        # Deterministic initial pick for this category, then progression is state-driven.
        base_index = index % len(progression)
        candidate = progression[base_index]
        if candidate == previous_motion and len(progression) > 1:
            candidate = progression[(base_index + 1) % len(progression)]
        return candidate

    @staticmethod
    def _build_emotional_state(segment: dict[str, Any], index: int) -> str:
        text = str(segment.get("text", "")).strip().lower()
        items = " ".join(
            str(item.get("text", "")).strip().lower()
            for item in segment.get("items", [])
        )
        source = f"{text} {items}"

        if index == 0:
            return "neutral setup"

        if index == 1:
            return "tension build"

        if any(word in source for word in ("pause", "still", "settles", "stop", "wait")):
            return "emotional release"

        if any(word in source for word in ("gaze", "look", "glance", "stare")):
            return "deepening emotional tension"

        if any(word in source for word in ("forward", "move", "walk", "step", "turn")):
            return "emotional escalation"

        return "emotional escalation"
