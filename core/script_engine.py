class ScriptEngine:
    def analyze(self, text: str) -> dict:
        text = text.lower()

        return {
            "has_character": any(k in text for k in ["i ", "she ", "he ", "we "]),
            "tone": self._detect_tone(text),
            "pace": self._detect_pace(text),
        }

    def _detect_tone(self, text: str) -> str:
        if any(k in text for k in ["fear", "dark", "alone"]):
            return "dark"
        if any(k in text for k in ["happy", "joy", "love"]):
            return "warm"
        return "neutral"

    def _detect_pace(self, text: str) -> str:
        if len(text.split()) < 100:
            return "slow"
        return "normal"