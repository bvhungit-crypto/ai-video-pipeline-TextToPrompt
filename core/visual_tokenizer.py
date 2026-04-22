from __future__ import annotations

from typing import Any


class VisualTokenizer:
    def tokenize(self, segment: dict[str, Any]) -> dict[str, Any]:
        state = segment.get("state", {})
        tokens: dict[str, Any] = {
            "subject": self._subject_action(segment=segment),
            "emotion": self._clean_text(
                segment.get("emotion", state.get("emotional_state", ""))
            ),
            "intent": self._clean_text(segment.get("intent", "")),
            "scene_goal": self._clean_text(segment.get("scene_goal", "")),
            "space": self._space(segment=segment),
            "behavior": self._behavior(segment=segment),
            "focus": self._clean_text(segment.get("cinematic_focus", "")),
            "shot_intent": self._shot_intent(segment=segment),
            "camera_shot": self._clean_text(state.get("camera", {}).get("shot", "")),
            "motion": self._clean_text(state.get("motion", "")),
            "style_constraints": segment.get("style_constraints", {}),
            "arc_stage": self._clean_text(segment.get("arc_stage", "")),
            "emotion_vector": segment.get("emotion_vector", {}),
            "shot_class": self._clean_text(segment.get("shot_class", "")),
            "shot_priority": self._clean_text(segment.get("director_brain", {}).get("shot_priority", "")),
            "director_brain": segment.get("director_brain", {}),
            "global_film_state": segment.get("global_film_state", {}),
        }
        return tokens

    @staticmethod
    def _clean_text(value: Any) -> str:
        return " ".join(str(value).strip().split()).rstrip(" .")

    def _subject_action(self, segment: dict[str, Any]) -> str:
        visual_behavior = self._clean_text(segment.get("visual_behavior", ""))
        if visual_behavior:
            return visual_behavior

        motion = self._clean_text(segment.get("state", {}).get("motion", "")).lower()
        focus = self._clean_text(segment.get("cinematic_focus", "")).lower()

        if "gaze" in motion:
            if "lower" in motion:
                return "her eyes drop and her chin follows a fraction behind"
            return "her eyes avoid contact as her head turns away slowly"
        if any(word in motion for word in ("forward", "moves", "moving")):
            return "she shifts forward half a step, shoulders held tight"
        if "turn" in motion:
            return "she turns slowly at the waist, keeping the rest of her body still"
        if any(word in motion for word in ("lift", "upward")):
            return "her hand rises slightly, then hesitates in the air"
        if any(word in motion for word in ("settles", "pause")):
            return "her weight shifts backward half a step as the movement fades"
        if "hands" in focus or "gesture" in focus:
            return "her fingers tighten slightly around the fabric as her posture firms"
        if "face" in focus or "expression" in focus:
            return "her jaw tightens slightly as her eyes hold steady for a beat"
        return "her hands stay close to her body as she shifts her weight with care"

    def _space(self, segment: dict[str, Any]) -> str:
        environment = self._clean_text(
            segment.get("state", {}).get("environment", {}).get("description", "")
        )
        if environment and "unified cinematic setting" not in environment:
            return environment

        focus = self._clean_text(segment.get("cinematic_focus", "")).lower()
        if "room" in focus or "space" in focus:
            return "quiet interior"
        if "face" in focus or "expression" in focus:
            return "intimate interior"
        return "intimate interior"

    def _behavior(self, segment: dict[str, Any]) -> str:
        visual_behavior = self._clean_text(segment.get("visual_behavior", ""))
        if visual_behavior:
            return visual_behavior

        emotion = self._clean_text(
            segment.get("emotion", segment.get("state", {}).get("emotional_state", ""))
        ).lower()

        if any(word in emotion for word in ("uncertainty", "hesitation", "guarded")):
            return "eyes dip away, jaw tightens, shoulders stay lifted"
        if any(word in emotion for word in ("tension", "pressure", "unease")):
            return "a held breath catches in the chest while the hands stay rigid"
        if any(word in emotion for word in ("resolve", "determination", "urgency")):
            return "balance shifts onto the front foot as the shoulders set"
        if any(word in emotion for word in ("release", "vulnerability", "fragile")):
            return "the shoulders ease slightly while the fingers finally loosen"
        return "posture stays compact, breath measured, hands held close"

    def _shot_intent(self, segment: dict[str, Any]) -> str:
        shot_intent = self._clean_text(segment.get("shot_intent", ""))
        if shot_intent:
            return shot_intent

        focus = self._clean_text(segment.get("cinematic_focus", "")).lower()
        scene_goal = self._clean_text(segment.get("scene_goal", "")).lower()

        if "face" in focus or "expression" in focus:
            return "hold for the smallest visible reaction"
        if "hands" in focus or "gesture" in focus or "posture" in focus:
            return "let physical restraint carry the beat"
        if "room" in focus or "space" in focus:
            return "keep the body small inside the room"
        if "release" in scene_goal or "clarity" in scene_goal:
            return "hold until the pressure begins to give way"
        return "hold on the first visible change"
