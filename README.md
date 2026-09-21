<p align="center"><strong>English</strong> · <a href="README.fr.md">Français</a></p>

<p align="center"><img src="assets/hero.svg" alt="FrameBudget — Find the encode that fits your constraints." width="100%"></p>

# FrameBudget

**Find the encode that fits your constraints.**

A proposed open-source FFmpeg optimizer for exploring the trade-offs between video size, measured quality, and encoding time.

> **In development.** This repository contains the initial specification and documentation. No executable release has shipped yet.


**Original repository: [GitLab](https://gitlab.elielaloum.com/elielaloum/framebudget)** · [Public GitHub mirror](https://github.com/elie-laloum/framebudget). The GitLab origin is private and requires access. Code changes are integrated in GitLab and synchronized to GitHub.


## Make encoding decisions visible

Choose a quality target and a search budget. FrameBudget should test candidate settings on representative segments, compare their outcomes, and explain the selected compromise before encoding the full file.

```text
Inspect → Sample → Explore settings → Compare trade-offs → Encode → Verify
```

## First release scope

- Python CLI calling FFmpeg and ffprobe.
- SDR input, preserved resolution, and libx264 encoding.
- A bounded search across CRF values and presets.
- Sample-based VMAF evaluation with an optional full-file quality verification.
- JSON and HTML reports listing settings, measurements, estimates, and decisions.

The search budget caps exploration; it is not a guarantee of total encoding time. Sample quality does not guarantee the same result across the entire video. If no candidate satisfies the constraints, the tool should report that outcome.

## What must make it useful

[ab-av1](https://github.com/alexheretic/ab-av1) already supports CRF search and size/time estimates. FrameBudget's proposed angle is budgeted exploration and an explicit comparison of quality, size, and time. The implementation must earn that distinction in reproducible comparisons.

## The demo we will ship

A redistributable video corpus, candidate results, a trade-off chart, the selected settings, and a verified final file. Record hardware, encoder versions, sample selection, and total search cost. [VMAF](https://github.com/Netflix/vmaf) is a quality metric, not a promise of visually identical output.

## Release requirements

Preserve originals, verify final decoding and duration, document audio and subtitle handling, and distinguish measured results from estimates. HDR and additional encoders come after the initial scope is validated.

## Help shape it

Useful early contributions: redistributable clips, benchmark reproductions, and difficult scenes. Installation instructions will be published after the supported FFmpeg configuration is verified.


---

[Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)
