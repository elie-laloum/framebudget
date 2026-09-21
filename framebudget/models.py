"""Versioned report contracts shared by search, encoding and rendering."""

from typing import NotRequired, TypedDict


class Stream(TypedDict):
    index: int
    type: str


class Media(TypedDict):
    duration: float
    width: int
    height: int
    video_index: int
    streams: list[Stream]


class Candidate(TypedDict):
    crf: int
    preset: str
    quality: float
    sample_scores: list[float]
    sample_bytes: int
    encode_seconds: float
    estimated_video_bytes: int


class SearchError(TypedDict):
    error: str
    crf: NotRequired[int]
    preset: NotRequired[str]


class SearchReport(TypedDict):
    schema_version: int
    input: str
    input_bytes: int
    input_mtime_ns: int
    media: Media
    ffmpeg: str
    metric: str
    target: float
    quality_aggregation: str
    search_budget_seconds: float
    search_seconds: float
    budget_exhausted: bool
    sample_offsets: list[float]
    sample_seconds: float
    candidates: list[Candidate]
    pareto: list[Candidate]
    selected: Candidate | None
    errors: list[SearchError]
    status: str
    notes: list[str]
    output: NotRequired[str]
    output_bytes: NotRequired[int]
    final_quality: NotRequired[float | None]
