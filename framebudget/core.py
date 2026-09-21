"""Compatibility exports; implementations live in focused modules."""

from .encoding import encode as encode
from .errors import BudgetError as BudgetError
from .media import probe as probe
from .metrics import quality_score as quality_score
from .process import run as run
from .reporting import html_report as html_report
from .sampling import sample_offsets as sample_offsets
from .search import search as search
from .selection import pareto as pareto
