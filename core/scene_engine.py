class SceneEngine:
    def enhance(self, segments: list[dict], mode: str = "character") -> list[dict]:
        for index, seg in enumerate(segments):
            if index == 0:
                seg["camera"] = "wide"
            elif index == 1:
                seg["camera"] = "medium"
            else:
                seg["camera"] = "close"
        return segments