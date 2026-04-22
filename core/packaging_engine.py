from __future__ import annotations

from math import ceil
from typing import Any


class PackagingEngine:
    SEGMENT_DURATION = 6
    MIN_OVERLAP_DURATION = 0.5
    MIN_CONSECUTIVE_REUSE_OVERLAP = 2.0

    def package(self, timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not timeline:
            return []

        sorted_timeline = self._normalize_timeline(timeline)
        max_end = max(item["end"] for item in sorted_timeline)
        segment_count = ceil(max_end / self.SEGMENT_DURATION)
        segments: list[dict[str, Any]] = []
        recently_used_item_ids: set[int] = set()

        for index in range(segment_count):
            segment_start = index * self.SEGMENT_DURATION
            segment_end = segment_start + self.SEGMENT_DURATION

            items: list[dict[str, Any]] = []

            for item in sorted_timeline:
                overlap_duration = self._overlap_duration(
                    item_start=float(item["start"]),
                    item_end=float(item["end"]),
                    segment_start=segment_start,
                    segment_end=segment_end,
                )

                if overlap_duration <= self.MIN_OVERLAP_DURATION:
                    continue

                if (
                    item["id"] in recently_used_item_ids
                    and overlap_duration < self.MIN_CONSECUTIVE_REUSE_OVERLAP
                ):
                    continue

                items.append(
                    {
                        "id": item["id"],
                        "text": item["text"],
                        "start": item["start"],
                        "end": item["end"],
                    }
                )

            if not items:
                recently_used_item_ids = set()
                continue

            segments.append(
                {
                    "start": segment_start,
                    "end": segment_end,
                    "duration": self.SEGMENT_DURATION,
                    "items": items,
                    "text": " ".join(item["text"] for item in items),
                    "density": len(items),
                    "duration_covered": sum(
                        self._overlap_duration(
                            item_start=item["start"],
                            item_end=item["end"],
                            segment_start=segment_start,
                            segment_end=segment_end,
                        )
                        for item in items
                    ),
                }
            )
            recently_used_item_ids = {item["id"] for item in items}

        return segments

    @staticmethod
    def _normalize_timeline(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized_items = [
            {
                "id": index,
                "text": str(item["text"]),
                "start": float(item["start"]),
                "end": float(item["end"]),
            }
            for index, item in enumerate(timeline)
        ]
        return sorted(normalized_items, key=lambda item: item["start"])

    @staticmethod
    def _overlap_duration(
        item_start: float,
        item_end: float,
        segment_start: float,
        segment_end: float,
    ) -> float:
        overlap_start = max(item_start, segment_start)
        overlap_end = min(item_end, segment_end)
        return max(0.0, overlap_end - overlap_start)
