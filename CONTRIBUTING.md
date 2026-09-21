# Contributing

Use Python 3.14; CI covers 3.12 and 3.14. Create a virtual environment and install the package and development tools:

```sh
python -m venv .venv
# Activate .venv for your shell.
python -m pip install -e '.[dev]'
python -m ruff check .
python -m ruff format --check .
python -m mypy framebudget
python -m unittest discover -s tests -v
python -m build
```

Install FFmpeg/ffprobe to run integration tests; set `FFMPEG`/`FFPROBE` to explicit binaries if needed. VMAF demos need an FFmpeg build with libvmaf. Tests never require downloaded media.

Read [architecture](docs/architecture.md). Keep metric interpretation and algorithm selection separate from subprocess details. Changes to reports or output publication require regression tests. Submit through GitHub; integration takes place in the private GitLab origin.
