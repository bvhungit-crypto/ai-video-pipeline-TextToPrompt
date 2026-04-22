from __future__ import annotations

from typing import Any


class EmotionalArcEngine:
    def enrich(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        enriched: list[dict[str, Any]] = []

        for index, segment in enumerate(segments):
            global_film_state = segment.get("global_film_state", {})
            director_brain = segment.get("director_brain", {})
            arc_map = global_film_state.get("arc_map", [])
            tension_curve = global_film_state.get("tension_curve", [])

            arc_stage = str(
                director_brain.get("narrative_stage", arc_map[index] if index < len(arc_map) else "setup")
            )
            tension_target = float(
                director_brain.get(
                    "tension_target",
                    tension_curve[index] if index < len(tension_curve) else 0.35,
                )
            )
            emotion_vector = self._emotion_vector(
                segment=segment,
                arc_stage=arc_stage,
                tension_target=tension_target,
            )
            enriched.append(
                {
                    **segment,
                    "arc_stage": arc_stage,
                    "emotion_vector": emotion_vector,
                }
            )

        return enriched

    @staticmethod
    def _emotion_vector(
        segment: dict[str, Any],
        arc_stage: str,
        tension_target: float,
    ) -> dict[str, float]:
        text = str(segment.get("text", "")).lower()
        motion = str(segment.get("state", {}).get("motion", "")).lower()
        source = f"{text} {motion}"
        continuity_memory = segment.get("continuity_memory", {})
        carried_tension = float(continuity_memory.get("current_spatial_tension", 0.35))

        tension = max(tension_target, carried_tension * 0.8)
        openness = max(0.12, 0.78 - tension)
        release = 0.08

        if any(word in source for word in ("gaze", "look", "glance", "stare")):
            tension += 0.05
        if any(word in source for word in ("move", "walk", "step", "turn", "approach")):
            tension += 0.06
        if any(word in source for word in ("pause", "still", "settles", "stop", "wait")):
            release += 0.22

        if arc_stage == "setup":
            release = 0.05
        elif arc_stage == "escalation":
            tension = max(tension, min(tension_target + 0.05, 0.82))
        elif arc_stage == "climax":
            tension = max(tension, 0.9)
            openness = min(openness, 0.24)
            release = max(release, 0.1)
        elif arc_stage == "resolution":
            tension = min(tension, 0.48)
            openness = max(openness, 0.5)
            release = max(release, 0.68)

        return {
            "tension": round(min(tension, 1.0), 2),
            "openness": round(min(openness, 1.0), 2),
            "release": round(min(release, 1.0), 2),
        }
