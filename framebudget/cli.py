import argparse
import json
from pathlib import Path
from .core import BudgetError, search, encode, html_report


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compare FFmpeg settings within a search budget.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, help='Optional final .mkv output; never overwritten')
    parser.add_argument('--report', type=Path, required=True, help='New JSON report path')
    parser.add_argument('--html', type=Path, help='Optional new HTML report path')
    parser.add_argument('--budget', type=float, default=60)
    parser.add_argument('--samples', type=int, default=3)
    parser.add_argument('--sample-seconds', type=float, default=2)
    parser.add_argument('--crfs', type=int, nargs='+', default=[20, 26, 32])
    parser.add_argument('--presets', nargs='+', default=['fast', 'medium'])
    parser.add_argument('--metric', choices=['vmaf', 'psnr'], default='vmaf')
    parser.add_argument('--min-quality', type=float, default=93)
    parser.add_argument('--verify-quality', action='store_true')
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    args = parser.parse_args(argv)
    try:
        paths = [p.resolve() for p in (args.input, args.report, args.html, args.output) if p]
        if len(paths) != len(set(paths)):
            raise BudgetError('Input, output and reports must have distinct paths')
        for p in (args.report, args.html, args.output):
            if p and p.exists():
                raise BudgetError(f'Refusing to overwrite {p}')
        report = search(args.input, ffmpeg=args.ffmpeg, ffprobe=args.ffprobe, budget=args.budget,
                        samples=args.samples, sample_seconds=args.sample_seconds, crfs=args.crfs,
                        presets=args.presets, metric=args.metric, min_quality=args.min_quality)
        if args.output and report['selected']:
            try:
                encode(report, args.output, ffmpeg=args.ffmpeg, ffprobe=args.ffprobe, verify_quality=args.verify_quality)
            except (BudgetError, OSError) as exc:
                report['status'] = 'verification_failed'
                report['errors'].append({'error': str(exc)})
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open('x', encoding='utf-8') as f:
            json.dump(report, f, indent=2, allow_nan=False)
        if args.html:
            args.html.parent.mkdir(parents=True, exist_ok=True)
            with args.html.open('x', encoding='utf-8') as f:
                f.write(html_report(report))
        print(f"{report['status']}: {len(report['candidates'])} candidates; report {args.report}")
        return 0 if report['status'] in {'selected', 'encoded'} else 1
    except (BudgetError, OSError, ValueError) as exc:
        print(f'framebudget: {exc}')
        return 2
