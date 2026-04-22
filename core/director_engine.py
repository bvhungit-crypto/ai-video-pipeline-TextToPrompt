from __future__ import annotations

import hashlib
from typing import Any


class DirectorEngine:
    def enrich(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not segments:
            return []

        total_segments = len(segments)
        enriched_segments: list[dict[str, Any]] = []

        for index, segment in enumerate(segments):
            emotion = self._emotion(segment=segment, index=index, total=total_segments)
            intent = self._intent(segment=segment, index=index, total=total_segments)
            scene_goal = self._scene_goal(segment=segment, index=index, total=total_segments)
            cinematic_focus = self._cinematic_focus(
                segment=segment,
                index=index,
                total=total_segments,
            )
            visual_behavior = self._emotion_to_visual_behavior(
                emotion=emotion,
                segment=segment,
                index=index,
            )
            camera_directive = self._intent_to_camera_directive(
                intent=intent,
                scene_goal=scene_goal,
                segment=segment,
                index=index,
            )
            shot_intent = self._shot_intent(
                cinematic_focus=cinematic_focus,
                scene_goal=scene_goal,
                segment=segment,
                index=index,
            )

            direction = {
                "emotion": emotion,
                "intent": intent,
                "scene_goal": scene_goal,
                "cinematic_focus": cinematic_focus,
                "visual_behavior": visual_behavior,
                "camera_directive": camera_directive,
                "shot_intent": shot_intent,
            }
            enriched_segments.append({**segment, **direction})

        return enriched_segments

    def _emotion(self, segment: dict[str, Any], index: int, total: int) -> str:
        motion = self._motion_text(segment)
        phase = self._phase(index=index, total=total)

        if "gaze" in motion:
            options = {
                "opening": (
                    "quiet uncertainty",
                    "guarded attention",
                ),
                "middle": (
                    "tightening tension",
                    "deepening unease",
                ),
                "closing": (
                    "contained vulnerability",
                    "pressure close to release",
                ),
            }
            return self._choose(options[phase], segment, "emotion-gaze")

        if any(word in motion for word in ("forward", "moving", "moves")):
            options = {
                "opening": (
                    "measured resolve",
                    "careful determination",
                ),
                "middle": (
                    "weighted resolve",
                    "pressure inside momentum",
                ),
                "closing": (
                    "committed urgency",
                    "resolve under strain",
                ),
            }
            return self._choose(options[phase], segment, "emotion-forward")

        if any(word in motion for word in ("turn", "lift", "pause", "settles")):
            options = {
                "opening": (
                    "held restraint",
                    "quiet hesitation",
                ),
                "middle": (
                    "nervous control",
                    "tension inside restraint",
                ),
                "closing": (
                    "fragile control",
                    "release under pressure",
                ),
            }
            return self._choose(options[phase], segment, "emotion-gesture")

        options = {
            "opening": (
                "neutral restraint",
                "quiet observation",
            ),
            "middle": (
                "growing tension",
                "deepening focus",
            ),
            "closing": (
                "emotional escalation",
                "pressure nearing release",
            ),
        }
        return self._choose(options[phase], segment, "emotion-default")

    def _intent(self, segment: dict[str, Any], index: int, total: int) -> str:
        motion = self._motion_text(segment)
        phase = self._phase(index=index, total=total)

        if "gaze" in motion:
            options = {
                "opening": (
                    "hold distance while attention settles",
                    "observe the first flicker of uncertainty",
                ),
                "middle": (
                    "draw closer as tension gathers",
                    "stay with the face as control tightens",
                ),
                "closing": (
                    "trap the viewer inside the hesitation",
                    "hold intimate pressure without release",
                ),
            }
            return self._choose(options[phase], segment, "intent-gaze")

        if any(word in motion for word in ("forward", "moving", "moves")):
            options = {
                "opening": (
                    "establish forward drive with restraint",
                    "let motion suggest controlled purpose",
                ),
                "middle": (
                    "compress space around the movement",
                    "make the progression feel harder won",
                ),
                "closing": (
                    "push the movement toward consequence",
                    "keep the momentum under emotional weight",
                ),
            }
            return self._choose(options[phase], segment, "intent-forward")

        options = {
            "opening": (
                "establish behavior before meaning becomes clear",
                "anchor the scene in physical detail",
            ),
            "middle": (
                "tighten attention around subtle change",
                "let tension emerge through small physical shifts",
            ),
            "closing": (
                "hold the frame where pressure becomes visible",
                "bring the emotional turn closer without breaking continuity",
            ),
        }
        return self._choose(options[phase], segment, "intent-default")

    def _scene_goal(self, segment: dict[str, Any], index: int, total: int) -> str:
        phase = self._phase(index=index, total=total)

        if phase == "opening":
            options = (
                "move from setup into engagement",
                "turn observation into felt tension",
            )
        elif phase == "middle":
            options = (
                "tighten the dramatic pressure",
                "deepen tension without release",
            )
        else:
            options = (
                "push the moment toward emotional release",
                "bring the scene to the edge of emotional clarity",
            )

        return self._choose(options, segment, "scene-goal")

    def _cinematic_focus(self, segment: dict[str, Any], index: int, total: int) -> str:
        camera_shot = (
            str(segment.get("state", {}).get("camera", {}).get("shot", "")).strip().lower()
        )
        motion = self._motion_text(segment)

        if camera_shot == "wide":
            options = (
                "the figure's position inside the room",
                "distance between body and surrounding space",
            )
            return self._choose(options, segment, "focus-wide")

        if camera_shot == "medium":
            if "gaze" in motion:
                options = (
                    "eyes, jaw, and restrained facial reaction",
                    "the face holding back visible reaction",
                )
            else:
                options = (
                    "small changes in posture and gesture",
                    "hands, shoulders, and shifting balance",
                )
            return self._choose(options, segment, "focus-medium")

        if camera_shot == "close":
            options = (
                "micro-expression under pressure",
                "tiny facial changes and held breath",
            )
            return self._choose(options, segment, "focus-close")

        options = (
            "the physical detail carrying the beat",
            "visible behavior under emotional pressure",
        )
        return self._choose(options, segment, "focus-default")

    def _emotion_to_visual_behavior(
        self,
        emotion: str,
        segment: dict[str, Any],
        index: int,
    ) -> str:
        lowered = emotion.lower()
        motion = self._motion_text(segment)

        if "uncertainty" in lowered or "hesitation" in lowered:
            options = (
                "eyes dip away as her jaw tightens for a beat",
                "her chin lowers slightly while her fingers hold still against the fabric",
                "she avoids direct eye contact and shifts her weight back a fraction",
            )
        elif "tension" in lowered or "pressure" in lowered:
            options = (
                "her shoulders lock subtly while her fingers press tighter into her sleeve",
                "a held breath settles in her chest as her mouth hardens for a moment",
                "her posture stiffens and her eyes stay fixed a fraction too long",
            )
        elif "resolve" in lowered or "determination" in lowered:
            options = (
                "she steps forward half a pace, shoulders set and hands controlled at her sides",
                "her balance shifts onto the front foot as her gaze steadies",
                "she leans into the movement with her hands held close and deliberate",
            )
        elif "release" in lowered or "vulnerability" in lowered:
            options = (
                "her shoulders ease slightly as her gaze drops out of contact",
                "a small release runs through her posture and her fingers loosen at last",
                "her face softens for an instant before she steadies again",
            )
        else:
            options = (
                "her fingers tighten slightly around the fabric as her posture firms",
                "she shifts her weight backward half a step without breaking the frame",
                "her head turns away slowly while her eyes avoid contact",
            )

        if "gaze" in motion:
            options = options + (
                "her eyes drift off the line of sight as the rest of her face stays controlled",
            )
        return self._choose(options, segment, f"visual-behavior-{index}")

    def _intent_to_camera_directive(
        self,
        intent: str,
        scene_goal: str,
        segment: dict[str, Any],
        index: int,
    ) -> str:
        camera_shot = (
            str(segment.get("state", {}).get("camera", {}).get("shot", "")).strip().lower()
        )
        lowered_intent = intent.lower()
        lowered_goal = scene_goal.lower()

        if camera_shot == "wide":
            if "engagement" in lowered_goal or "observation" in lowered_goal:
                options = (
                    "wide shot, slow drift holding the subject against the room",
                    "wide shot, gentle lateral drift to keep tension between subject and space",
                )
            else:
                options = (
                    "wide shot, slight handheld drift reflecting unstable control",
                    "wide shot, restrained forward creep as the room begins to close in",
                )
            return self._choose(options, segment, f"camera-wide-{index}")

        if camera_shot == "medium":
            if "face" in lowered_intent or "closer" in lowered_intent or "tension" in lowered_goal:
                options = (
                    "medium shot, slow push-in as if pulled by her hesitation",
                    "medium shot, gentle forward movement as tension builds around her",
                )
            else:
                options = (
                    "medium shot, slight handheld drift reflecting emotional instability",
                    "medium shot, subtle creep inward to compress the space around her",
                )
            return self._choose(options, segment, f"camera-medium-{index}")

        if camera_shot == "close":
            options = (
                "close shot, steady hold listening for the smallest change in her face",
                "close shot, delicate handheld drift reflecting emotional instability",
            )
            return self._choose(options, segment, f"camera-close-{index}")

        options = (
            "medium shot, gentle forward movement as tension builds between subject and space",
            "medium shot, slight handheld drift to keep the emotion unsettled",
        )
        return self._choose(options, segment, f"camera-default-{index}")

    def _shot_intent(
        self,
        cinematic_focus: str,
        scene_goal: str,
        segment: dict[str, Any],
        index: int,
    ) -> str:
        lowered_focus = cinematic_focus.lower()
        lowered_goal = scene_goal.lower()

        if "face" in lowered_focus or "micro-expression" in lowered_focus:
            options = (
                "hold on the face until the internal shift becomes visible",
                "stay close enough for the smallest reaction to carry the beat",
            )
        elif "hands" in lowered_focus or "gesture" in lowered_focus or "posture" in lowered_focus:
            options = (
                "let posture and hand tension define the beat",
                "use physical restraint to carry the dramatic change",
            )
        elif "room" in lowered_focus or "space" in lowered_focus:
            options = (
                "keep the pressure between the body and the room in frame",
                "use surrounding space to make the subject feel exposed",
            )
        elif "release" in lowered_goal or "clarity" in lowered_goal:
            options = (
                "hold the frame until pressure starts to give way",
                "keep the image tight as the scene approaches release",
            )
        else:
            options = (
                "let visible behavior carry the dramatic turn",
                "keep the frame on the detail that changes the emotional balance",
            )

        return self._choose(options, segment, f"shot-intent-{index}")

    @staticmethod
    def _phase(index: int, total: int) -> str:
        if total <= 1:
            return "opening"
        if index == 0:
            return "opening"
        if index == 1:
            return "middle"
        return "closing"

    @staticmethod
    def _motion_text(segment: dict[str, Any]) -> str:
        state = segment.get("state", {})
        return str(state.get("motion", "")).strip().lower()

    @staticmethod
    def _key(segment: dict[str, Any], label: str) -> str:
        start = segment.get("start", "")
        end = segment.get("end", "")
        text = segment.get("text", "")
        return f"{label}|{start}|{end}|{text}"

    def _choose(
        self,
        options: tuple[str, ...],
        segment: dict[str, Any],
        label: str,
    ) -> str:
        digest = hashlib.md5(self._key(segment, label).encode("utf-8")).hexdigest()
        return options[int(digest[:8], 16) % len(options)]
