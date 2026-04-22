from __future__ import annotations

from typing import Any


class ContinuityMemoryEngine:
    def enrich(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        previous_emotion = "neutral"
        previous_posture = "centered"
        previous_spatial_tension = 0.3
        enriched: list[dict[str, Any]] = []

        for segment in segments:
            motion = str(segment.get("state", {}).get("motion", "")).lower()
            emotion = str(segment.get("emotional_state", "")).lower()
            density = int(segment.get("density", 0))

            posture = self._posture_state(motion=motion, density=density, previous=previous_posture)
            spatial_tension = self._spatial_tension(
                segment=segment,
                previous=previous_spatial_tension,
            )

            continuity_memory = {
                "previous_emotion": previous_emotion,
                "current_emotion": emotion or previous_emotion,
                "previous_posture": previous_posture,
                "current_posture": posture,
                "previous_spatial_tension": round(previous_spatial_tension, 2),
                "current_spatial_tension": round(spatial_tension, 2),
            }

            enriched.append(
                {
                    **segment,
                    "continuity_memory": continuity_memory,
                }
            )

            previous_emotion = continuity_memory["current_emotion"]
            previous_posture = posture
            previous_spatial_tension = spatial_tension

        return enriched

    @staticmethod
    def _posture_state(motion: str, density: int, previous: str) -> str:
        if any(word in motion for word in ("forward", "approach", "step", "walk")):
            return "advancing"
        if any(word in motion for word in ("turn", "pivot", "rotate")):
            return "coiled"
        if any(word in motion for word in ("pause", "still", "settles", "stop")):
            return "releasing"
        if any(word in motion for word in ("gaze", "look", "glance")):
            return "guarded"
        if density >= 3:
            return "compressed"
        return previous

    @staticmethod
    def _spatial_tension(segment: dict[str, Any], previous: float) -> float:
        density = int(segment.get("density", 0))
        covered = float(segment.get("duration_covered", 0.0))
        base = 0.25 + min(density * 0.12, 0.36) + min(covered / 12.0, 0.24)
        blended = (previous * 0.45) + (base * 0.55)
        return min(blended, 1.0)
