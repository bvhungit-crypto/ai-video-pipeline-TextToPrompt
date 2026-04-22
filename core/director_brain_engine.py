from __future__ import annotations

from typing import Any


class DirectorBrainEngine:
    def enrich(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        global_film_state = self._global_film_state(segments)
        enriched: list[dict[str, Any]] = []

        for index, segment in enumerate(segments):
            narrative_stage = global_film_state["arc_map"][index]
            tension_target = global_film_state["tension_curve"][index]
            cinematic_priority = self._cinematic_priority(
                segment=segment,
                narrative_stage=narrative_stage,
                tension_target=tension_target,
            )
            director_brain = {
                "narrative_stage": narrative_stage,
                "cinematic_priority": cinematic_priority,
                "shot_priority": cinematic_priority,
                "tension_target": tension_target,
                "narrative_direction": global_film_state["narrative_direction"],
                "body_emphasis": self._body_emphasis(
                    segment=segment,
                    narrative_stage=narrative_stage,
                    priority=cinematic_priority,
                ),
                "space_emphasis": self._space_emphasis(
                    segment=segment,
                    narrative_stage=narrative_stage,
                    priority=cinematic_priority,
                ),
                "camera_intent": self._camera_intent(
                    segment=segment,
                    narrative_stage=narrative_stage,
                    priority=cinematic_priority,
                ),
            }

            enriched.append(
                {
                    **segment,
                    "global_film_state": global_film_state,
                    "director_brain": director_brain,
                }
            )

        return enriched

    def _global_film_state(self, segments: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(segments)
        arc_map = [self._narrative_stage(index=index, total=total) for index in range(total)]
        tension_curve = [self._tension_target(index=index, total=total) for index in range(total)]
        density_profile = [int(segment.get("density", 0)) for segment in segments]

        return {
            "character_continuity": "locked",
            "location_continuity": "locked",
            "narrative_direction": "single continuous dramatic rise with late release",
            "arc_map": arc_map,
            "tension_curve": tension_curve,
            "density_profile": density_profile,
        }

    @staticmethod
    def _narrative_stage(index: int, total: int) -> str:
        if total <= 1 or index == 0:
            return "setup"
        if total == 2:
            return "resolution" if index == 1 else "setup"
        if index < total - 2:
            return "escalation"
        if index == total - 2:
            return "climax"
        return "resolution"

    @staticmethod
    def _tension_target(index: int, total: int) -> float:
        if total <= 1:
            return 0.35
        progress = index / (total - 1)
        if progress == 0:
            return 0.28
        if progress < 0.75:
            return round(0.28 + (progress * 0.72), 2)
        if progress < 1.0:
            return round(0.82 + ((progress - 0.75) * 0.48), 2)
        return 0.42

    @staticmethod
    def _cinematic_priority(
        segment: dict[str, Any],
        narrative_stage: str,
        tension_target: float,
    ) -> str:
        density = int(segment.get("density", 0))
        motion = str(segment.get("state", {}).get("motion", "")).lower()

        if narrative_stage == "climax":
            return "A"
        if tension_target >= 0.75 or density >= 3:
            return "A"
        if any(word in motion for word in ("turn", "approach", "step", "gaze")):
            return "B"
        if narrative_stage == "resolution":
            return "C"
        return "B"

    @staticmethod
    def _body_emphasis(segment: dict[str, Any], narrative_stage: str, priority: str) -> str:
        motion = str(segment.get("state", {}).get("motion", "")).lower()

        if "gaze" in motion:
            return "eyes_jaw"
        if any(word in motion for word in ("forward", "step", "walk", "move")):
            return "weight_shoulders"
        if any(word in motion for word in ("turn", "pivot", "rotate")):
            return "torso_shoulders"
        if priority == "A":
            return "hands_posture"
        if narrative_stage == "resolution":
            return "shoulders_hands"
        return "hands_posture"

    @staticmethod
    def _space_emphasis(segment: dict[str, Any], narrative_stage: str, priority: str) -> str:
        camera = str(segment.get("state", {}).get("camera", {}).get("shot", "")).lower()

        if camera == "wide":
            return "negative_space"
        if camera == "close":
            return "facial_field"
        if narrative_stage == "climax":
            return "compressed_depth"
        if priority == "A":
            return "compressed_depth"
        if narrative_stage == "resolution":
            return "softened_depth"
        return "upper_body_field"

    @staticmethod
    def _camera_intent(segment: dict[str, Any], narrative_stage: str, priority: str) -> str:
        motion = str(segment.get("state", {}).get("motion", "")).lower()

        if narrative_stage == "setup":
            return "observe"
        if narrative_stage == "climax":
            return "press_in"
        if narrative_stage == "resolution":
            return "hold_release"
        if "gaze" in motion:
            return "draw_close"
        if priority == "A":
            return "tighten"
        return "track_subtle_shift"
