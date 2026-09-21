from __future__ import annotations

import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


class BudgetError(Exception):
    pass


def run(argv, *, timeout=300, cwd=None):
    if timeout <= 0:
        raise BudgetError("Search budget exhausted")
    try:
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired as exc:
        raise BudgetError("Command exceeded its time budget") from exc
    except OSError as exc:
        raise BudgetError(str(exc)) from exc
    if result.returncode:
        raise BudgetError("Command failed: " + result.stderr[-1800:])
    return result


def probe(source, ffprobe="ffprobe"):
    data = json.loads(run([ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)]).stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")), None)
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
    return {"duration": duration, "width": video["width"], "height": video["height"],
            "video_index": video["index"], "streams": [{"index": s["index"], "type": s["codec_type"]} for s in streams]}


def sample_offsets(duration, count, seconds):
    if count < 1 or seconds <= 0 or duration <= 0:
        raise BudgetError("Sample count, length and duration must be positive")
    length = min(duration, seconds)
    span = max(0, duration - length)
    if count == 1 or span == 0:
        return [span / 2], length
    return [i * span / (count - 1) for i in range(count)], length


def pareto(candidates):
    def dominates(a, b):
        av = (a["sample_bytes"], a["encode_seconds"], -a["quality"])
        bv = (b["sample_bytes"], b["encode_seconds"], -b["quality"])
        return all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv))
    return [c for c in candidates if not any(d is not c and dominates(d, c) for d in candidates)]


def quality_score(ffmpeg, reference, distorted, metric, *, timeout, cwd):
    alignment = "[0:v]setpts=PTS-STARTPTS[d];[1:v]setpts=PTS-STARTPTS[r];"
    measurement = "[d][r]libvmaf=n_threads=1" if metric == "vmaf" else "[d][r]psnr"
    result = run([ffmpeg, "-hide_banner", "-nostdin", "-i", str(distorted), "-i", str(reference),
                  "-lavfi", alignment + measurement, "-an", "-f", "null", "-"], timeout=timeout, cwd=cwd)
    pattern = r"VMAF score:\s*([\d.]+)" if metric == "vmaf" else r"average:([\d.]+|inf)"
    scores = re.findall(pattern, result.stderr)
    if not scores:
        raise BudgetError(f"Could not read {metric} score from FFmpeg")
    value = float(scores[-1])
    # JSON has no infinity; 100 dB represents the exact-match sentinel for PSNR.
    return 100.0 if math.isinf(value) else value


def search(source, *, ffmpeg="ffmpeg", ffprobe="ffprobe", budget=60, samples=3,
           sample_seconds=2, crfs=(20, 26, 32), presets=("fast", "medium"), metric="vmaf", min_quality=93):
    source = Path(source).resolve(strict=True)
    if not math.isfinite(budget) or budget <= 0 or not math.isfinite(min_quality):
        raise BudgetError("Budget must be positive and quality must be finite")
    if metric not in {"vmaf", "psnr"} or not 0 <= min_quality <= 100:
        raise BudgetError("Unsupported metric or quality target")
    allowed = {"ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"}
    if not crfs or not presets or any(c < 0 or c > 51 for c in crfs) or any(p not in allowed for p in presets):
        raise BudgetError("Invalid CRF values or presets")
    metadata = probe(source, ffprobe)
    version = run([ffmpeg, "-version"]).stdout.splitlines()[0]
    filters = run([ffmpeg, "-hide_banner", "-filters"]).stdout
    if metric == "vmaf" and "libvmaf" not in filters:
        raise BudgetError("This FFmpeg build lacks libvmaf; select --metric psnr with a PSNR target instead")
    offsets, length = sample_offsets(metadata["duration"], samples, sample_seconds)
    start = time.monotonic()
    deadline = start + budget
    candidates, errors = [], []
    exhausted = False
    with tempfile.TemporaryDirectory(prefix="framebudget-") as directory:
        folder = Path(directory)
        references = []
        try:
            for i, offset in enumerate(offsets):
                ref = folder / f"reference-{i}.mkv"
                run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-ss", str(offset), "-i", str(source),
                     "-t", str(length), "-map", f"0:{metadata['video_index']}", "-an", "-sn", "-c:v", "ffv1", "-pix_fmt", "yuv420p", str(ref)],
                    timeout=deadline-time.monotonic())
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
                            run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(ref), "-an", "-c:v", "libx264",
                                 "-threads", "1", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", str(encoded)], timeout=deadline-time.monotonic())
                            elapsed += time.monotonic() - before
                            size += encoded.stat().st_size
                            scores.append(quality_score(ffmpeg, ref, encoded, metric, timeout=deadline-time.monotonic(), cwd=directory))
                        candidates.append({"crf": crf, "preset": preset, "quality": min(scores), "sample_scores": scores,
                                           "sample_bytes": size, "encode_seconds": round(elapsed, 4),
                                           "estimated_video_bytes": round(size * metadata["duration"] / (len(references) * length))})
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
    selected = min(feasible, key=lambda c: (c["sample_bytes"], c["encode_seconds"])) if feasible else None
    return {"schema_version": 1, "input": str(source), "input_bytes": source.stat().st_size,
            "input_mtime_ns": source.stat().st_mtime_ns, "media": metadata, "ffmpeg": version,
            "metric": metric, "target": min_quality, "quality_aggregation": "minimum of sample means",
            "search_budget_seconds": budget, "search_seconds": round(time.monotonic()-start, 4),
            "budget_exhausted": exhausted, "sample_offsets": offsets, "sample_seconds": length,
            "candidates": candidates, "pareto": frontier, "selected": selected, "errors": errors,
            "status": "selected" if selected else "no_feasible_candidate",
            "notes": ["Samples estimate full-file quality; they do not guarantee it.",
                      "Video size estimates include sample container overhead but exclude copied audio/subtitles.",
                      "Search budget includes extraction, sample encoding and scoring, not probing or final encoding."]}


def encode(report, output, *, ffmpeg="ffmpeg", ffprobe="ffprobe", verify_quality=False, timeout=3600):
    output = Path(output).resolve()
    source = Path(report["input"])
    if output == source or output.exists():
        raise BudgetError("Output already exists or is the input; refusing to overwrite")
    if output.suffix.lower() != '.mkv':
        raise BudgetError("This version writes .mkv files to preserve supported audio and subtitle streams")
    if source.stat().st_size != report["input_bytes"] or source.stat().st_mtime_ns != report["input_mtime_ns"]:
        raise BudgetError("Input changed after sampling")
    chosen = report["selected"]
    if chosen is None:
        raise BudgetError("No feasible encoding candidate")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".framebudget-", dir=output.parent) as directory:
        temp = Path(directory) / 'output.mkv'
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(source),
             "-map", f"0:{report['media']['video_index']}", "-map", "0:a?", "-map", "0:s?", "-c", "copy", "-c:v:0", "libx264",
             "-threads", "1", "-preset", chosen["preset"], "-crf", str(chosen["crf"]), "-pix_fmt", "yuv420p", str(temp)], timeout=timeout)
        run([ffmpeg, "-hide_banner", "-v", "error", "-xerror", "-nostdin", "-i", str(temp), "-map", "0:v:0", "-map", "0:a?", "-f", "null", "-"], timeout=timeout)
        final = probe(temp, ffprobe)
        if abs(final["duration"] - report["media"]["duration"]) > max(.15, report["media"]["duration"] * .01):
            raise BudgetError("Encoded duration differs from the source")
        for kind in ("audio", "subtitle"):
            if sum(s["type"] == kind for s in report["media"]["streams"]) != sum(s["type"] == kind for s in final["streams"]):
                raise BudgetError(f"Missing {kind} stream in the encoded output")
        score = quality_score(ffmpeg, source, temp, report["metric"], timeout=timeout, cwd=directory) if verify_quality else None
        if score is not None and score < report["target"]:
            raise BudgetError(f"Final quality {score:.3f} is below target {report['target']}")
        # Hard-link publication is atomic and fails if another process created the destination.
        os.link(temp, output)
    report["output"] = str(output)
    report["output_bytes"] = output.stat().st_size
    report["final_quality"] = score
    report["status"] = "encoded"
    return report


def html_report(report):
    rows = ''.join(f"<tr><td>{c['preset']}</td><td>{c['crf']}</td><td>{c['quality']:.3f}</td><td>{c['sample_bytes']:,}</td><td>{c['encode_seconds']:.3f}s</td></tr>" for c in report['candidates'])
    escape = lambda value: html.escape(str(value))
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>FrameBudget report</title>
<style>body{{background:#101722;color:#edf1f6;font:16px system-ui;max-width:1000px;margin:60px auto;padding:24px}}h1{{font-size:56px;color:#ffc573}}table{{width:100%;border-collapse:collapse}}th,td{{padding:14px;text-align:left;border-bottom:1px solid #334}}p{{line-height:1.7}}code{{color:#ffc573}}.muted{{color:#adbacb}}</style>
<p class="muted">ENCODING EXPERIMENT</p><h1>FrameBudget</h1><p>{escape(report['input'])}</p><p>Status: <code>{escape(report['status'])}</code> · Metric: {escape(report['metric'])} · Target: {report['target']} · Search: {report['search_seconds']}s</p>
<table><tr><th>Preset</th><th>CRF</th><th>Min sample score</th><th>Sample bytes</th><th>Encode time</th></tr>{rows}</table>
<p>Selection: {escape(report['selected'])}</p><p class="muted">Measured on samples. Full-file size and quality may differ. The JSON report includes candidates, Pareto frontier, errors and verification details.</p></html>'''
