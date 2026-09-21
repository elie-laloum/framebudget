import math
import re
from pathlib import Path

from .errors import BudgetError
from .process import run


def quality_score(
    ffmpeg: str,
    reference: str | Path,
    distorted: str | Path,
    metric: str,
    *,
    timeout: float,
    cwd: str | Path,
) -> float:
    alignment = "[0:v]setpts=PTS-STARTPTS[d];[1:v]setpts=PTS-STARTPTS[r];"
    measurement = "[d][r]libvmaf=n_threads=1" if metric == "vmaf" else "[d][r]psnr"
    result = run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostdin",
            "-i",
            str(distorted),
            "-i",
            str(reference),
            "-lavfi",
            alignment + measurement,
            "-an",
            "-f",
            "null",
            "-",
        ],
        timeout=timeout,
        cwd=cwd,
    )
    pattern = r"VMAF score:\s*([\d.]+)" if metric == "vmaf" else r"average:([\d.]+|inf)"
    scores = re.findall(pattern, result.stderr)
    if not scores:
        raise BudgetError(f"Could not read {metric} score from FFmpeg")
    value = float(scores[-1])
    # JSON has no infinity; 100 dB represents the exact-match sentinel for PSNR.
    if math.isnan(value):
        raise BudgetError("Non-finite quality score")
    return 100.0 if math.isinf(value) else value
