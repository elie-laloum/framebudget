from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .errors import BudgetError
from .media import probe
from .metrics import quality_score
from .models import SearchReport
from .process import run


def encode(
    report: SearchReport,
    output: str | Path,
    *,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    verify_quality: bool = False,
    timeout: float = 3600,
) -> SearchReport:
    output = Path(output).resolve()
    source = Path(report["input"])
    if output == source or output.exists():
        raise BudgetError("Output already exists or is the input; refusing to overwrite")
    if output.suffix.lower() != ".mkv":
        raise BudgetError(
            "This version writes .mkv files to preserve supported audio and subtitle streams"
        )
    if (
        source.stat().st_size != report["input_bytes"]
        or source.stat().st_mtime_ns != report["input_mtime_ns"]
    ):
        raise BudgetError("Input changed after sampling")
    chosen = report["selected"]
    if chosen is None:
        raise BudgetError("No feasible encoding candidate")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".framebudget-", dir=output.parent) as directory:
        temp = Path(directory) / "output.mkv"
        run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-i",
                str(source),
                "-map",
                f"0:{report['media']['video_index']}",
                "-map",
                "0:a?",
                "-map",
                "0:s?",
                "-c",
                "copy",
                "-c:v:0",
                "libx264",
                "-threads",
                "1",
                "-preset",
                chosen["preset"],
                "-crf",
                str(chosen["crf"]),
                "-pix_fmt",
                "yuv420p",
                str(temp),
            ],
            timeout=timeout,
        )
        run(
            [
                ffmpeg,
                "-hide_banner",
                "-v",
                "error",
                "-xerror",
                "-nostdin",
                "-i",
                str(temp),
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-f",
                "null",
                "-",
            ],
            timeout=timeout,
        )
        final = probe(temp, ffprobe)
        if abs(final["duration"] - report["media"]["duration"]) > max(
            0.15, report["media"]["duration"] * 0.01
        ):
            raise BudgetError("Encoded duration differs from the source")
        for kind in ("audio", "subtitle"):
            if sum(s["type"] == kind for s in report["media"]["streams"]) != sum(
                s["type"] == kind for s in final["streams"]
            ):
                raise BudgetError(f"Missing {kind} stream in the encoded output")
        score = (
            quality_score(ffmpeg, source, temp, report["metric"], timeout=timeout, cwd=directory)
            if verify_quality
            else None
        )
        if score is not None and score < report["target"]:
            raise BudgetError(f"Final quality {score:.3f} is below target {report['target']}")
        # Hard-link publication is atomic and fails if another process created the destination.
        os.link(temp, output)
    report["output"] = str(output)
    report["output_bytes"] = output.stat().st_size
    report["final_quality"] = score
    report["status"] = "encoded"
    return report
