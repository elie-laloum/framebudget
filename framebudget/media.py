from __future__ import annotations

import json
import math
from pathlib import Path

from .errors import BudgetError
from .models import Media
from .process import run


def probe(source: str | Path, ffprobe: str = "ffprobe") -> Media:
    data = json.loads(
        run(
            [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)]
        ).stdout
    )
    streams = data.get("streams", [])
    video = next(
        (
            s
            for s in streams
            if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")
        ),
        None,
    )
    if video is None:
        raise BudgetError("Input has no video stream")
    if sum(s.get("codec_type") == "video" for s in streams) != 1:
        raise BudgetError("This version requires exactly one video stream, without cover artwork")
    duration = float(data.get("format", {}).get("duration", video.get("duration", 0)))
    if not math.isfinite(duration) or duration <= 0:
        raise BudgetError("Input duration must be known and positive")
    if video.get("color_transfer") in {"smpte2084", "arib-std-b67"}:
        raise BudgetError("HDR input is not supported in this version")
    if video["width"] % 2 or video["height"] % 2:
        raise BudgetError("libx264 yuv420p output requires even dimensions")
    return {
        "duration": duration,
        "width": video["width"],
        "height": video["height"],
        "video_index": video["index"],
        "streams": [{"index": s["index"], "type": s["codec_type"]} for s in streams],
    }
