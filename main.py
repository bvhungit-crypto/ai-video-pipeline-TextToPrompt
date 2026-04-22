from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from core import TimelineEngine
from core.auto_fix_engine import AutoFixEngine
from core.meta_controller import MetaController
from pipeline import AnimationPipeline, DocumentaryPipeline, MontagePipeline


TIMECODE_PATTERN = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)


def parse_srt_timestamp(value: str) -> float:
    hours, minutes, seconds_millis = value.split(":")
    seconds, millis = seconds_millis.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis) / 1000
    )


def srt_to_timeline(srt_text: str) -> list[dict[str, Any]]:
    blocks = re.split(r"\r?\n\r?\n+", srt_text.strip())
    timeline: list[dict[str, Any]] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue

        timecode_line_index = 1 if "-->" in lines[1] else 0
        if timecode_line_index >= len(lines):
            continue

        match = TIMECODE_PATTERN.fullmatch(lines[timecode_line_index])
        if not match:
            continue

        text_lines = lines[timecode_line_index + 1 :]
        text = " ".join(text_lines).strip()
        if not text:
            continue

        timeline.append(
            {
                "start": parse_srt_timestamp(match.group("start")),
                "end": parse_srt_timestamp(match.group("end")),
                "text": text,
            }
        )

    return timeline


def build_timeline(engine: TimelineEngine, srt_text: str) -> list[dict[str, Any]]:
    if hasattr(engine, "build"):
        return engine.build(srt_text)  # type: ignore[no-any-return]
    return srt_to_timeline(srt_text)


def run_pipeline(input_path: Path, output_path: Path) -> list[dict[str, Any]]:
    print("Loading SRT...")
    srt_text = input_path.read_text(encoding="utf-8")
    srt_line_count = len([line for line in srt_text.splitlines() if line.strip()])
    print(f"Loaded {srt_line_count} non-empty SRT lines.")
    if not srt_text.strip():
        print("Warning: input SRT file is empty.")

    style = "cinematic_dark"
    mode = "character"
    print("FINAL STYLE:", style)
    print("FINAL MODE:", mode)
    pipeline_type = MetaController.select_pipeline(style, mode)
    print("PIPELINE TYPE:", pipeline_type)

    timeline_engine = TimelineEngine()
    auto_fix_engine = AutoFixEngine()
    pipeline_runner = _pipeline_runner(pipeline_type=pipeline_type, style=style, mode=mode)

    print("Building timeline...")
    timeline = build_timeline(timeline_engine, srt_text)
    if not timeline:
        print("Warning: timeline is empty.")

    print("Generating prompts...")
    output = pipeline_runner.run(timeline, style=style, mode=mode)
    output = _apply_auto_fix(output, auto_fix_engine)
    if not output:
        print("Warning: no prompts were generated.")

    print("Writing output file...")
    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Output file: {output_path.resolve()}")
    return output


def main() -> None:
    print("Pipeline starting...")
    input_path = Path("data/input/input.srt")
    output_path = Path("data/output/output.json")

    os.makedirs(input_path.parent, exist_ok=True)
    os.makedirs(output_path.parent, exist_ok=True)

    print(f"Resolved input path: {input_path.resolve()}")
    print(f"Resolved output path: {output_path.resolve()}")

    if not input_path.exists():
        print("Missing input.srt")
        sys.exit(1)

    run_pipeline(input_path=input_path, output_path=output_path)
    print("Done")

def run_pipeline_from_text(
    srt_text: str,
    style: str,
    mode: str,
):
    print("FINAL STYLE:", style)
    print("FINAL MODE:", mode)
    pipeline_type = MetaController.select_pipeline(style, mode)
    print("PIPELINE TYPE:", pipeline_type)
    timeline_engine = TimelineEngine()
    auto_fix_engine = AutoFixEngine()
    pipeline_runner = _pipeline_runner(pipeline_type=pipeline_type, style=style, mode=mode)

    timeline = build_timeline(timeline_engine, srt_text)
    output = pipeline_runner.run(timeline, style=style, mode=mode)
    output = _apply_auto_fix(output, auto_fix_engine)
    return output


def _pipeline_runner(pipeline_type: str, style: str, mode: str):
    if pipeline_type == "animation":
        return AnimationPipeline(style=style)
    if pipeline_type == "montage":
        return MontagePipeline(style=style)
    return DocumentaryPipeline(style=style, mode=mode)


def _apply_auto_fix(output: list[dict[str, Any]], auto_fix_engine: AutoFixEngine) -> list[dict[str, Any]]:
    fixed: list[dict[str, Any]] = []
    human_words = ("she", "he", "person", "man", "woman")
    for item in output:
        prompt = str(item.get("prompt", ""))
        has_human = any(word in prompt.lower() for word in human_words)
        fixed_prompt = auto_fix_engine.fix(prompt, has_human=has_human)
        fixed.append({**item, "prompt": fixed_prompt})
    return fixed


if __name__ == "__main__":
    main()
