"""Shared utility functions."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def ensure_parent(path: Path) -> None:
    """Ensure that a file's parent directory exists."""

    path.parent.mkdir(parents=True, exist_ok=True)


def standardize_text(value: object) -> str:
    """Normalize display text to title case with single spaces."""

    if pd.isna(value):
        return ""
    text = re.sub(r"\s+", " ", str(value).strip())
    return text.title()


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two series while protecting against zero denominators."""

    result = numerator.div(denominator.mask(denominator == 0))
    return result.fillna(0)


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Scale a numeric series to 0-100."""

    min_value = series.min()
    max_value = series.max()
    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - min_value) / (max_value - min_value) * 100).clip(0, 100)
