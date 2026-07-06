"""Statistical analysis for business growth data."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config.config import AppConfig
from src.logger import get_logger
from src.utils import ensure_parent, safe_divide


@dataclass
class BusinessAnalyzer:
    """Create statistical summaries and rankings."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)

    def descriptive_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.select_dtypes("number").describe().T

    def correlation_matrix(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.select_dtypes("number").corr(numeric_only=True)

    def industry_summary(self, data: pd.DataFrame) -> pd.DataFrame:
        summary = (
            data.groupby("Industry", as_index=False)
            .agg(
                Companies=("CompanyID", "count"),
                AverageBGPI=("BGPI", "mean"),
                AverageRevenue=("MonthlyRevenue", "mean"),
                AverageProfitMargin=("ProfitMargin", "mean"),
                AverageCustomerSatisfaction=("CustomerSatisfaction", "mean"),
                AverageInnovation=("ProductInnovation", "mean"),
                AverageRisk=("RiskScore", "mean"),
            )
            .sort_values("AverageBGPI", ascending=False)
        )
        return summary.round(2)

    def company_rankings(self, data: pd.DataFrame, top_n: int = 20) -> dict[str, pd.DataFrame]:
        return {
            "growth_potential": data.nlargest(top_n, "BGPI"),
            "profitability": data.nlargest(top_n, "ProfitMargin"),
            "innovation": data.nlargest(top_n, "ProductInnovation"),
            "customer_satisfaction": data.nlargest(top_n, "CustomerSatisfaction"),
            "bottom_growth": data.nsmallest(top_n, "BGPI"),
        }

    def revenue_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        revenue = data.copy()
        revenue["RevenuePerEmployee"] = safe_divide(
            revenue["MonthlyRevenue"], revenue["Employees"]
        )
        return revenue[
            [
                "CompanyID",
                "CompanyName",
                "Industry",
                "MonthlyRevenue",
                "RevenueGrowth",
                "RevenuePerEmployee",
                "BGPI",
            ]
        ].sort_values("MonthlyRevenue", ascending=False)

    def profitability_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        profit = data.copy()
        profit["MonthlyProfit"] = profit["MonthlyRevenue"] - profit["MonthlyExpenses"]
        return profit[
            [
                "CompanyID",
                "CompanyName",
                "Industry",
                "MonthlyProfit",
                "ProfitMargin",
                "BGPI",
            ]
        ].sort_values("MonthlyProfit", ascending=False)

    def customer_retention_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        retention = data.copy()
        retention["RetentionRate"] = safe_divide(
            retention["RepeatCustomers"],
            retention["RepeatCustomers"] + retention["NewCustomers"],
        ) * 100
        return retention[
            [
                "CompanyID",
                "CompanyName",
                "Industry",
                "RetentionRate",
                "CustomerSatisfaction",
                "BGPI",
            ]
        ].sort_values("RetentionRate", ascending=False)

    def export_outputs(self, data: pd.DataFrame) -> dict[str, Path]:
        """Export core analysis outputs to processed CSV files."""

        outputs = {
            "industry_summary": self.config.industry_summary_path,
            "company_summary": self.config.company_summary_path,
            "growth_report": self.config.growth_report_path,
            "correlation_matrix": self.config.processed_dir / "correlation_matrix.csv",
            "descriptive_statistics": self.config.processed_dir / "descriptive_statistics.csv",
        }
        for path in outputs.values():
            ensure_parent(path)

        self.industry_summary(data).to_csv(outputs["industry_summary"], index=False)
        self.revenue_analysis(data).head(100).to_csv(outputs["company_summary"], index=False)
        data.sort_values("BGPI", ascending=False).to_csv(outputs["growth_report"], index=False)
        self.correlation_matrix(data).to_csv(outputs["correlation_matrix"])
        self.descriptive_statistics(data).to_csv(outputs["descriptive_statistics"])
        self.logger.info("Exported statistical analysis outputs.")
        return outputs
