import html

from .models import SearchReport


def html_report(report: SearchReport) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(c['preset'])}</td><td>{c['crf']}</td><td>{c['quality']:.3f}</td><td>{c['sample_bytes']:,}</td><td>{c['encode_seconds']:.3f}s</td></tr>"
        for c in report["candidates"]
    )

    def escape(value: object) -> str:
        return html.escape(str(value))

    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>FrameBudget report</title>
<style>body{{background:#101722;color:#edf1f6;font:16px system-ui;max-width:1000px;margin:60px auto;padding:24px}}h1{{font-size:56px;color:#ffc573}}table{{width:100%;border-collapse:collapse}}th,td{{padding:14px;text-align:left;border-bottom:1px solid #334}}p{{line-height:1.7}}code{{color:#ffc573}}.muted{{color:#adbacb}}</style>
<p class="muted">ENCODING EXPERIMENT</p><h1>FrameBudget</h1><p>{escape(report["input"])}</p><p>Status: <code>{escape(report["status"])}</code> · Metric: {escape(report["metric"])} · Target: {report["target"]} · Search: {report["search_seconds"]}s</p>
<table><tr><th>Preset</th><th>CRF</th><th>Min sample score</th><th>Sample bytes</th><th>Encode time</th></tr>{rows}</table>
<p>Selection: {escape(report["selected"])}</p><p class="muted">Measured on samples. Full-file size and quality may differ. The JSON report includes candidates, Pareto frontier, errors and verification details.</p></html>"""
