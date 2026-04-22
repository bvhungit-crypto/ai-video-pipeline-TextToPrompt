from __future__ import annotations

import hashlib


class CameraReasoningEngine:
    def derive(self, tokens: dict[str, str]) -> str:
        emotion = tokens.get("emotion", "").lower()
        intent = tokens.get("intent", "").lower()
        scene_goal = tokens.get("scene_goal", "").lower()
        focus = tokens.get("focus", "").lower()
        shot = tokens.get("camera_shot", "").lower()

        options = self._options(
            emotion=emotion,
            intent=intent,
            scene_goal=scene_goal,
            focus=focus,
            shot=shot,
        )
        return self._choose(options, self._key(tokens))

    def _options(
        self,
        emotion: str,
        intent: str,
        scene_goal: str,
        focus: str,
        shot: str,
    ) -> tuple[str, ...]:
        if any(word in emotion for word in ("uncertainty", "hesitation", "guarded")):
            return (
                "slow push-in as if the camera is drawn by her hesitation",
                "slight handheld drift reflecting emotional instability",
                "gentle inward movement following her reluctance to meet the moment",
            )

        if any(word in emotion for word in ("tension", "pressure", "unease", "escalation")):
            return (
                "gentle forward movement as tension builds between subject and space",
                "slow creeping move that compresses the air around her",
                "subtle handheld drift keeping the frame emotionally unsettled",
            )

        if any(word in emotion for word in ("resolve", "determination", "urgency")):
            return (
                "measured forward glide tracking her controlled momentum",
                "firm, steady move with the subject as resolve takes shape",
                "restrained dolly movement that lets the action claim the frame",
            )

        if any(word in emotion for word in ("release", "vulnerability", "fragile")):
            return (
                "steady hold waiting for the release to register in the body",
                "barely perceptible drift as pressure starts to loosen",
                "quiet locked frame holding the change without interruption",
            )

        if "room" in focus or "space" in focus or shot == "wide":
            return (
                "slow drift holding tension between the body and the room",
                "measured lateral movement keeping the space emotionally active",
                "restrained wide movement letting the room press back on the subject",
            )

        if "face" in focus or "expression" in focus or shot == "close":
            return (
                "steady close hold listening for the smallest change in her face",
                "delicate inward drift toward the held expression",
                "quiet close framing with a barely moving handheld pulse",
            )

        if "gesture" in focus or "hands" in focus or "posture" in focus or shot == "medium":
            return (
                "subtle inward creep staying with posture and hand tension",
                "measured medium movement holding the body under pressure",
                "gentle camera drift following the controlled physical shift",
            )

        if "release" in scene_goal or "clarity" in scene_goal:
            return (
                "steady hold as the scene edges toward release",
                "gentle forward movement closing the distance before release",
                "restrained drift holding the frame just before clarity arrives",
            )

        if "engagement" in scene_goal or "tension" in scene_goal:
            return (
                "slow push-in tightening the scene without breaking continuity",
                "gentle forward movement letting pressure gather in the frame",
                "subtle handheld motion keeping the emotional line unstable",
            )

        if "closer" in intent or "face" in intent:
            return (
                "slow push-in bringing the viewer closer to the held reaction",
                "delicate forward movement narrowing the distance to the subject",
                "restrained inward move guided by the subject's uncertainty",
            )

        return (
            "gentle camera drift keeping the frame under quiet pressure",
            "slow inward movement holding the emotional line steady",
            "restrained handheld movement preserving the scene's unease",
        )

    @staticmethod
    def _key(tokens: dict[str, str]) -> str:
        return "|".join(
            [
                tokens.get("subject", ""),
                tokens.get("emotion", ""),
                tokens.get("intent", ""),
                tokens.get("scene_goal", ""),
                tokens.get("space", ""),
                tokens.get("focus", ""),
                tokens.get("camera_shot", ""),
            ]
        )

    @staticmethod
    def _choose(options: tuple[str, ...], key: str) -> str:
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return options[int(digest[:8], 16) % len(options)]
