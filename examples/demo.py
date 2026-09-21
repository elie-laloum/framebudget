"""Generate a tiny local video, search settings, and verify the final encode."""

import json
import os
import tempfile
from pathlib import Path

from framebudget.core import encode, html_report, run, search

folder = Path(tempfile.mkdtemp(prefix="framebudget-demo-"))
ffmpeg = os.environ.get("FFMPEG", "ffmpeg")
ffprobe = os.environ.get("FFPROBE", "ffprobe")
source = folder / "input.mkv"
run(
    [
        ffmpeg,
        "-v",
        "error",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=size=320x180:rate=24",
        "-t",
        "3",
        "-c:v",
        "ffv1",
        str(source),
    ]
)
metric = os.environ.get("FRAMEBUDGET_METRIC", "vmaf")
report = search(
    source,
    ffmpeg=ffmpeg,
    ffprobe=ffprobe,
    metric=metric,
    min_quality=80 if metric == "vmaf" else 25,
    crfs=[18, 28, 38],
    presets=["fast"],
    samples=2,
    sample_seconds=0.5,
    budget=60,
)
if report["selected"]:
    encode(report, folder / "output.mkv", ffmpeg=ffmpeg, ffprobe=ffprobe, verify_quality=True)
(folder / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(folder / "report.html").write_text(html_report(report), encoding="utf-8")
print(
    json.dumps(
        {
            "status": report["status"],
            "metric": metric,
            "candidates": len(report["candidates"]),
            "selected": report["selected"],
            "final_quality": report.get("final_quality"),
            "report": str(folder / "report.html"),
        },
        indent=2,
    )
)
raise SystemExit(0 if report["status"] == "encoded" else 1)
