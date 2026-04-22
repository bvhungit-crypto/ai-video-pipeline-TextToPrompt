from __future__ import annotations

from typing import Any


class StoryboardEngine:
    def build(self, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []

        for index, segment in enumerate(segments, start=1):
            frames.append(
                {
                    "frame": index,
                    "start": segment["start"],
                    "end": segment["end"],
                    "prompt": segment["prompt"],
                    "shot_class": segment.get("shot_class", ""),
                    "arc_stage": segment.get("arc_stage", ""),
                }
            )

        return frames
