"""Data cleaning module."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config.config import AppConfig
from src.logger import get_logger
from src.utils import ensure_parent, standardize_text


@dataclass
class DataCleaner:
    """Clean, validate, and export business datasets."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)

    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned copy of the input data."""

        cleaned = data.copy()
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates(subset=["CompanyID"])
        self.logger.info("Removed %s duplicate company rows.", before - len(cleaned))

        text_columns = ["CompanyID", "CompanyName", "Industry", "Country"]
        for column in text_columns:
            cleaned[column] = cleaned[column].apply(standardize_text)
        cleaned["CompanyID"] = cleaned["CompanyID"].str.upper()

        numeric_columns = list(self.config.numeric_ranges)
        for column in numeric_columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
            cleaned[column] = self._fill_numeric(cleaned[column])
            lower, upper = self.config.numeric_ranges[column]
            cleaned[column] = cleaned[column].clip(lower=lower, upper=upper)
            cleaned[column] = self._cap_outliers(cleaned[column])

        for column in text_columns:
            if cleaned[column].eq("").any():
                mode = cleaned.loc[cleaned[column].ne(""), column].mode()
                fallback = mode.iloc[0] if not mode.empty else "Unknown"
                cleaned[column] = cleaned[column].replace("", fallback)

        cleaned["ProfitMargin"] = (
            (cleaned["MonthlyRevenue"] - cleaned["MonthlyExpenses"])
            / cleaned["MonthlyRevenue"].mask(cleaned["MonthlyRevenue"] == 0)
            * 100
        ).fillna(0).clip(-100, 100)

        self.logger.info("Cleaned dataset shape: %s.", cleaned.shape)
        return cleaned

    def export(self, data: pd.DataFrame, path: Path | None = None) -> Path:
        """Save cleaned data to CSV."""

        output_path = path or self.config.cleaned_dataset_path
        ensure_parent(output_path)
        data.to_csv(output_path, index=False)
        self.logger.info("Saved cleaned dataset to %s.", output_path)
        return output_path

    @staticmethod
    def _fill_numeric(series: pd.Series) -> pd.Series:
        median = series.median()
        if pd.isna(median):
            median = 0
        return series.fillna(median)

    @staticmethod
    def _cap_outliers(series: pd.Series) -> pd.Series:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            return series
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return series.clip(lower=lower, upper=upper)
