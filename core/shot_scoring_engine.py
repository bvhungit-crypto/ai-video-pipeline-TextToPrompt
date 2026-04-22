from __future__ import annotations

from typing import Any


class ShotScoringEngine:
    def enrich(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        previous_motion = ""
        previous_tension = 0.0
        previous_camera = ""
        enriched: list[dict[str, Any]] = []

        for segment in segments:
            motion = str(segment.get("state", {}).get("motion", "")).strip().lower()
            camera = str(segment.get("state", {}).get("camera", {}).get("shot", "")).strip().lower()
            vector = segment.get("emotion_vector", {})
            tension = float(vector.get("tension", 0.0))
            director_brain = segment.get("director_brain", {})
            priority = str(director_brain.get("shot_priority", director_brain.get("cinematic_priority", "B"))).upper()

            motion_change = 1.0 if motion and motion != previous_motion else 0.0
            emotional_shift = abs(tension - previous_tension)
            camera_evolution = 1.0 if camera and camera != previous_camera else 0.45 if camera else 0.0

            priority_weight = {"A": 0.75, "B": 0.4, "C": 0.1}.get(priority, 0.4)
            score = motion_change + emotional_shift + camera_evolution + priority_weight
            shot_class = self._shot_class(score=score, priority=priority)

            enriched.append(
                {
                    **segment,
                    "shot_score": round(score, 2),
                    "shot_class": shot_class,
                }
            )

            previous_motion = motion
            previous_tension = tension
            previous_camera = camera

        return enriched

    @staticmethod
    def _shot_class(score: float, priority: str) -> str:
        if priority in {"A", "B", "C"}:
            return priority
        if score >= 2.0:
            return "A"
        if score >= 1.15:
            return "B"
        return "C"
