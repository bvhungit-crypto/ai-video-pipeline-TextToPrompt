from __future__ import annotations


class PromptAssemblerV4:
    def assemble(
        self,
        style: str,
        subject_action: str,
        environment: str,
        behavior: str,
        camera_directive: str,
        shot_intent: str,
        lighting: str = "",
        composition: str = "",
        camera: str = "",
        motion_style: str = "",
        mood: str = "",
        duration: str = "Duration: 6 seconds",
    ) -> str:
        parts = [
            self._clean(style),
            self._clean(subject_action),
            self._clean(lighting),
            self._clean(composition),
            self._clean(camera),
            self._clean(environment),
            self._clean(motion_style),
            self._clean(behavior),
            self._clean(camera_directive),
            self._clean(mood),
            self._clean(shot_intent),
            self._clean(duration),
        ]

        deduped: list[str] = []
        seen: set[str] = set()
        for part in parts:
            if not part:
                continue
            key = part.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(part)

        return "\n\n".join(deduped)

    @staticmethod
    def _clean(value: str) -> str:
        cleaned = " ".join(str(value).strip().split())
        cleaned = cleaned.strip(" ,;.")
        if not cleaned:
            return ""
        if cleaned.lower().startswith("duration:"):
            return cleaned
        return cleaned[0].upper() + cleaned[1:]
