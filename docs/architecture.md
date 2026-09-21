# Architecture

The stable `framebudget.core` facade re-exports the public functions. Implementation is split by responsibility:

| Module | Responsibility |
| --- | --- |
| `models.py` | Typed versioned report contracts. |
| `sampling.py`, `selection.py` | Pure sampling and Pareto operations. |
| `process.py`, `media.py`, `metrics.py` | Bounded commands, probe validation and metric parsing. |
| `search.py` | Time-budgeted candidate exploration. |
| `encoding.py` | Final encode, verification and atomic no-overwrite publication. |
| `reporting.py`, `cli.py` | HTML presentation and CLI. |

Reports keep schema version 1. Sampling remains an estimate, never a guarantee. The final encode preserves supported audio/subtitle streams and only publishes after verification. Algorithm tests are deterministic; FFmpeg integration tests generate their own short input and exercise real encoding.

Python 3.14 is the development baseline; Python 3.12+ remains supported. Ruff covers formatting and linting. Mypy checks every package module in strict mode.
