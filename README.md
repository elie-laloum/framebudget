<p align="right"><a href="README.fr.md">Français</a></p>
<img src="assets/cover-v2.png" alt="FrameBudget — Spend less time guessing your next encode." width="100%">

[![CI](https://img.shields.io/github/actions/workflow/status/elie-laloum/framebudget/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/elie-laloum/framebudget/actions/workflows/ci.yml) [![License](https://img.shields.io/badge/license-MIT-586475?style=flat-square)](LICENSE)

**Compare H.264 settings on sampled scenes, choose a measured size–quality tradeoff, and verify the final encode.**

Python 3.12+ · FFmpeg · VMAF · [Quick start](#quick-start) · [How it works](#how-it-works) · [Boundaries](#boundaries)

## See it in action

<a href="assets/demo.mp4"><img src="assets/demo.gif" alt="FrameBudget — recorded demonstration" width="100%"></a>

<sub>Replay of a real demo run, with explanatory annotations and timing edited for readability.</sub>

[Watch the MP4](assets/demo.mp4) · [Reproduce this demo](docs/demo.md)

## Why it exists

### Search within a budget
Explore an explicit CRF/preset grid until the search budget expires. Incomplete candidates never become winners.

### See the tradeoffs
JSON and standalone HTML reports show quality, sample size, encoding time and the Pareto frontier.

### Verify the output
Optional full-file quality measurement complements decode, duration and audio/subtitle count checks before publishing the output.

## Quick start

```sh
git clone https://github.com/elie-laloum/framebudget.git
cd framebudget
python -m pip install .
python -m unittest discover -s tests
python examples/demo.py
```

Clone and run from source; these commands do not assume a package has been published to a registry.

## How it works

`Sample → encode → score → compare → verify`

A generated three-second clip exercises real FFmpeg encoding and VMAF scoring. On the development run, CRF 28 / fast was selected from three candidates: minimum sample score 92.76, final-file VMAF 94.48 against a target of 80. These are fixture results, not general compression claims.

## Use it on your project

```sh
framebudget input.mp4 --report result.json --html result.html --output result.mkv --budget 60 --min-quality 93 --verify-quality
```

Use `--crfs 20 26 32 --presets fast medium` to define the candidates and `--samples 3 --sample-seconds 2` to define the sample coverage. The selected candidate has the smallest sampled output among those meeting the minimum quality target on every sampled scene.

A run returns status 1 if no candidate meets the target or final verification fails; the report explains why. Status 2 means invalid input or configuration. Use `FFMPEG` and `FFPROBE` environment variables for the demo, or `--ffmpeg` / `--ffprobe` for the CLI.

## Boundaries

Requires FFmpeg with libx264 and libvmaf, plus ffprobe. PSNR is available explicitly with --metric psnr --min-quality 35; its units differ from VMAF. v0.1 targets SDR, even-sized, single-video inputs and writes MKV. Sampling cannot guarantee whole-file quality. The search budget covers extraction, sample encoding and scoring; probing and final encoding are separate. Files are never overwritten.

## Development

See the [module map](docs/architecture.md) and [contribution workflow](CONTRIBUTING.md).


Run `python -m unittest discover -s tests`. FFmpeg integration tests exercise actual encoding, full verification, an impossible quality target and budget exhaustion. They are skipped if FFmpeg is unavailable.

[Contributing](CONTRIBUTING.md) · [Roadmap](ROADMAP.md) · [MIT license](LICENSE)

[GitLab origin](https://gitlab.elielaloum.com/elielaloum/framebudget) · [GitHub mirror](https://github.com/elie-laloum/framebudget)

The private GitLab repository is the source of record. This public mirror receives synchronized changes; GitLab access is required to view the origin.
