from __future__ import annotations


class DirectorStyleEngine:
    PRESETS: dict[str, dict[str, str]] = {
        "nolan": {
            "style_suffix": "clean contrast, architectural tension",
            "camera_bias": "precise inward pressure",
            "space_bias": "structured negative space",
        },
        "villeneuve": {
            "style_suffix": "atmospheric scale, restrained movement",
            "camera_bias": "slow volumetric drift",
            "space_bias": "depth-heavy spatial isolation",
        },
        "a24": {
            "style_suffix": "intimate texture, fragile proximity",
            "camera_bias": "close observational drift",
            "space_bias": "lived-in interior compression",
        },
    }

    def __init__(self, preset: str = "villeneuve") -> None:
        self._preset = preset.lower()

    def enrich(self, segments: list[dict[str, object]]) -> list[dict[str, object]]:
        preset = self.PRESETS.get(self._preset, self.PRESETS["villeneuve"])
        return [
            {
                **segment,
                "style_preset": self._preset,
                "style_constraints": preset,
            }
            for segment in segments
        ]
