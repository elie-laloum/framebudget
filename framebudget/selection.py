from collections.abc import Sequence

from .models import Candidate


def pareto(candidates: Sequence[Candidate]) -> list[Candidate]:
    def dominates(a: Candidate, b: Candidate) -> bool:
        av = (a["sample_bytes"], a["encode_seconds"], -a["quality"])
        bv = (b["sample_bytes"], b["encode_seconds"], -b["quality"])
        return all(x <= y for x, y in zip(av, bv, strict=True)) and any(
            x < y for x, y in zip(av, bv, strict=True)
        )

    return [c for c in candidates if not any(d is not c and dominates(d, c) for d in candidates)]
