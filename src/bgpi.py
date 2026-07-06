"""Business Growth Potential Index engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config.config import AppConfig
from src.logger import get_logger
from src.utils import ensure_parent, min_max_normalize, safe_divide


@dataclass
class BGPICalculator:
    """Calculate BGPI, risk, and growth category."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Append BGPI outputs to a company dataset."""

        scored = data.copy()
        repeat_rate = safe_divide(
            scored["RepeatCustomers"],
            scored["RepeatCustomers"] + scored["NewCustomers"],
        ) * 100
        scored["RepeatCustomerRate"] = repeat_rate.clip(0, 100)
        raw_score = (
            scored["ProfitMargin"] * 0.30
            + scored["RevenueGrowth"] * 0.25
            + (scored["CustomerSatisfaction"] * 10) * 0.20
            + (scored["ProductInnovation"] * 10) * 0.15
            + scored["RepeatCustomerRate"] * 0.10
            - scored["EmployeeTurnover"] * 0.10
        )
        scored["BGPI"] = min_max_normalize(raw_score).round(2)
        scored["RiskScore"] = (100 - scored["BGPI"]).round(2)
        scored["GrowthCategory"] = scored["BGPI"].apply(self.classify_growth)
        self.logger.info("Calculated BGPI for %s companies.", len(scored))
        return scored

    @staticmethod
    def classify_growth(score: float) -> str:
        """Classify a normalized BGPI score."""

        if score >= 75:
            return "High Growth"
        if score >= 55:
            return "Stable"
        if score >= 35:
            return "Emerging"
        return "At Risk"

    def export(self, data: pd.DataFrame, path: Path | None = None) -> Path:
        """Export scored company data."""

        output_path = path or self.config.bgpi_scores_path
        ensure_parent(output_path)
        data.to_csv(output_path, index=False)
        self.logger.info("Saved BGPI results to %s.", output_path)
        return output_path
