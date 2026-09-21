from __future__ import annotations

import math
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path

from .errors import BudgetError
from .media import probe
from .metrics import quality_score
from .models import Candidate, SearchError, SearchReport
from .process import run
from .sampling import sample_offsets
from .selection import pareto


def search(
    source: str | Path,
    *,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    budget: float = 60,
    samples: int = 3,
    sample_seconds: float = 2,
    crfs: Sequence[int] = (20, 26, 32),
    presets: Sequence[str] = ("fast", "medium"),
    metric: str = "vmaf",
    min_quality: float = 93,
) -> SearchReport:
    source = Path(source).resolve(strict=True)
    if not math.isfinite(budget) or budget <= 0 or not math.isfinite(min_quality):
        raise BudgetError("Budget must be positive and quality must be finite")
    if metric not in {"vmaf", "psnr"} or not 0 <= min_quality <= 100:
        raise BudgetError("Unsupported metric or quality target")
    allowed = {
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    }
    if (
        not crfs
        or not presets
        or any(not isinstance(c, int) or isinstance(c, bool) or c < 0 or c > 51 for c in crfs)
        or any(p not in allowed for p in presets)
    ):
        raise BudgetError("Invalid CRF values or presets")
    metadata = probe(source, ffprobe)
    version = run([ffmpeg, "-version"]).stdout.splitlines()[0]
    filters = run([ffmpeg, "-hide_banner", "-filters"]).stdout
    if metric == "vmaf" and "libvmaf" not in filters:
        raise BudgetError(
            "This FFmpeg build lacks libvmaf; select --metric psnr with a PSNR target instead"
        )
    offsets, length = sample_offsets(metadata["duration"], samples, sample_seconds)
    start = time.monotonic()
    deadline = start + budget
    candidates: list[Candidate] = []
    errors: list[SearchError] = []
    exhausted = False
    with tempfile.TemporaryDirectory(prefix="framebudget-") as directory:
        folder = Path(directory)
        references = []
        try:
            for i, offset in enumerate(offsets):
                ref = folder / f"reference-{i}.mkv"
                run(
                    [
                        ffmpeg,
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-nostdin",
                        "-ss",
                        str(offset),
                        "-i",
                        str(source),
                        "-t",
                        str(length),
                        "-map",
                        f"0:{metadata['video_index']}",
                        "-an",
                        "-sn",
                        "-c:v",
                        "ffv1",
                        "-pix_fmt",
                        "yuv420p",
                        str(ref),
                    ],
                    timeout=deadline - time.monotonic(),
                )
                references.append(ref)
            # Interleave presets at each CRF to compare across the explored grid.
            for crf in crfs:
                for preset in presets:
                    if time.monotonic() >= deadline:
                        exhausted = True
                        break
                    scores, size, elapsed = [], 0, 0.0
                    try:
                        for i, ref in enumerate(references):
                            encoded = folder / f"candidate-{crf}-{preset}-{i}.mkv"
                            before = time.monotonic()
                            run(
                                [
                                    ffmpeg,
                                    "-hide_banner",
                                    "-loglevel",
                                    "error",
                                    "-nostdin",
                                    "-i",
                                    str(ref),
                                    "-an",
                                    "-c:v",
                                    "libx264",
                                    "-threads",
                                    "1",
                                    "-preset",
                                    preset,
                                    "-crf",
                                    str(crf),
                                    "-pix_fmt",
                                    "yuv420p",
                                    str(encoded),
                                ],
                                timeout=deadline - time.monotonic(),
                            )
                            elapsed += time.monotonic() - before
                            size += encoded.stat().st_size
                            scores.append(
                                quality_score(
                                    ffmpeg,
                                    ref,
                                    encoded,
                                    metric,
                                    timeout=deadline - time.monotonic(),
                                    cwd=directory,
                                )
                            )
                        candidates.append(
                            {
                                "crf": crf,
                                "preset": preset,
                                "quality": min(scores),
                                "sample_scores": scores,
                                "sample_bytes": size,
                                "encode_seconds": round(elapsed, 4),
                                "estimated_video_bytes": round(
                                    size * metadata["duration"] / (len(references) * length)
                                ),
                            }
                        )
                    except BudgetError as exc:
                        errors.append({"crf": crf, "preset": preset, "error": str(exc)})
                        if time.monotonic() >= deadline:
                            exhausted = True
                            break
                if exhausted:
                    break
        except BudgetError as exc:
            errors.append({"error": str(exc)})
            exhausted = time.monotonic() >= deadline
    frontier = pareto(candidates)
    feasible = [c for c in candidates if c["quality"] >= min_quality]
    selected = (
        min(feasible, key=lambda c: (c["sample_bytes"], c["encode_seconds"])) if feasible else None
    )
    return {
        "schema_version": 1,
        "input": str(source),
        "input_bytes": source.stat().st_size,
        "input_mtime_ns": source.stat().st_mtime_ns,
        "media": metadata,
        "ffmpeg": version,
        "metric": metric,
        "target": min_quality,
        "quality_aggregation": "minimum of sample means",
        "search_budget_seconds": budget,
        "search_seconds": round(time.monotonic() - start, 4),
        "budget_exhausted": exhausted,
        "sample_offsets": offsets,
        "sample_seconds": length,
        "candidates": candidates,
        "pareto": frontier,
        "selected": selected,
        "errors": errors,
        "status": "selected" if selected else "no_feasible_candidate",
        "notes": [
            "Samples estimate full-file quality; they do not guarantee it.",
            "Video size estimates include sample container overhead but exclude copied audio/subtitles.",
            "Search budget includes extraction, sample encoding and scoring, not probing or final encoding.",
        ],
    }
