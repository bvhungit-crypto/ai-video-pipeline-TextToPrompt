from __future__ import annotations

import re


class CameraImperfectionEngine:
    REPLACEMENTS = (
        (r"\bslow push-?in\b", "subtle handheld drift"),
        (r"\bpush-?in\b", "subtle forward drift"),
        (r"\bperfectly stable\b", "slightly unstable"),
        (r"\bsteady cinematic movement\b", "minor handheld instability"),
    )

    def apply(self, prompt: str) -> str:
        output = prompt
        for pattern, replacement in self.REPLACEMENTS:
            output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
        return output
