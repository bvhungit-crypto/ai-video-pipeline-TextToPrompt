class EmotionEngine:
    def build_arc(self, segments: list[dict], mode: str = "character") -> list[dict]:
        if mode == "montage":
            for seg in segments:
                seg["emotion_stage"] = "informational"
            return segments

        total = len(segments)

        for i, seg in enumerate(segments):
            progress = i / max(total - 1, 1)

            if progress < 0.3:
                seg["emotion_stage"] = "build"
            elif progress < 0.7:
                seg["emotion_stage"] = "tension"
            else:
                seg["emotion_stage"] = "release"

        return segments