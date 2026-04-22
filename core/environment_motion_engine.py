from __future__ import annotations

import random


class EnvironmentMotionEngine:
    CANDIDATES = (
        "Dust particles cross a narrow light beam.",
        "Light flicker appears on the back wall.",
        "A loose paper corner shifts slightly.",
        "Small shadow movement appears near the shelf edge.",
        "A cable end swings slightly above the floor.",
    )

    def inject(self, prompt: str, used_lines: set[str] | None = None) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        if not lines:
            return prompt

        used = used_lines if used_lines is not None else set()
        available = [line for line in self.CANDIDATES if line.lower() not in used]
        choice = random.choice(available or self.CANDIDATES)
        used.add(choice.lower())

        duration_index = next(
            (idx for idx, line in enumerate(lines) if line.lower().startswith("duration:")),
            len(lines),
        )
        lines.insert(duration_index, choice)

        deduped: list[str] = []
        seen: set[str] = set()
        for line in lines:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(line)
        return "\n\n".join(deduped)
