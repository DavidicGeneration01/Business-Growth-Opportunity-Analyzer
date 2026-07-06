"""Visualization module using Matplotlib and Seaborn."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config.config import AppConfig
from src.analysis import BusinessAnalyzer
from src.logger import get_logger


@dataclass
class BusinessVisualizer:
    """Generate professional PNG charts."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)
        sns.set_theme(style="whitegrid", palette="Set2")
        self.analyzer = BusinessAnalyzer(self.config)

    def generate_all(self, data: pd.DataFrame) -> list[Path]:
        """Generate the required chart set."""

        self.config.charts_dir.mkdir(parents=True, exist_ok=True)
        chart_specs = [
            ("bgpi_ranking.png", self._bgpi_ranking),
            ("revenue_distribution.png", self._revenue_distribution),
            ("profit_margin_distribution.png", self._profit_margin_distribution),
            ("industry_comparison.png", self._industry_comparison),
            ("customer_satisfaction.png", self._customer_satisfaction),
            ("marketing_vs_revenue.png", self._marketing_vs_revenue),
            ("revenue_growth_trend.png", self._revenue_growth_trend),
            ("employee_turnover.png", self._employee_turnover),
            ("innovation_score.png", self._innovation_score),
            ("correlation_heatmap.png", self._correlation_heatmap),
            ("top_20_companies.png", self._top_20_companies),
            ("bottom_20_companies.png", self._bottom_20_companies),
        ]
        paths: list[Path] = []
        for filename, chart_func in chart_specs:
            path = self.config.charts_dir / filename
            chart_func(data, path)
            paths.append(path)
        self.logger.info("Generated %s charts.", len(paths))
        return paths

    def _save(self, path: Path, title: str) -> None:
        plt.title(title, fontsize=14, weight="bold")
        plt.tight_layout()
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()

    def _bgpi_ranking(self, data: pd.DataFrame, path: Path) -> None:
        top = data.nlargest(15, "BGPI")
        plt.figure(figsize=(11, 7))
        sns.barplot(data=top, y="CompanyName", x="BGPI", hue="Industry", dodge=False)
        plt.legend(loc="lower right", fontsize=8)
        self._save(path, "BGPI Ranking - Top 15 Companies")

    def _revenue_distribution(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(10, 6))
        sns.histplot(data["MonthlyRevenue"], bins=40, kde=True)
        self._save(path, "Monthly Revenue Distribution")

    def _profit_margin_distribution(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(10, 6))
        sns.histplot(data["ProfitMargin"], bins=35, kde=True)
        self._save(path, "Profit Margin Distribution")

    def _industry_comparison(self, data: pd.DataFrame, path: Path) -> None:
        summary = self.analyzer.industry_summary(data)
        plt.figure(figsize=(11, 6))
        sns.barplot(data=summary, x="Industry", y="AverageBGPI")
        plt.xticks(rotation=35, ha="right")
        self._save(path, "Average BGPI by Industry")

    def _customer_satisfaction(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=data, x="Industry", y="CustomerSatisfaction")
        plt.xticks(rotation=35, ha="right")
        self._save(path, "Customer Satisfaction by Industry")

    def _marketing_vs_revenue(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=data, x="MarketingBudget", y="MonthlyRevenue", hue="Industry", alpha=0.65)
        plt.legend(fontsize=7, ncol=2)
        self._save(path, "Marketing Budget vs Monthly Revenue")

    def _revenue_growth_trend(self, data: pd.DataFrame, path: Path) -> None:
        grouped = data.groupby("YearsOperating", as_index=False)["RevenueGrowth"].mean()
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=grouped, x="YearsOperating", y="RevenueGrowth", marker="o")
        self._save(path, "Average Revenue Growth by Years Operating")

    def _employee_turnover(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=data, x="Industry", y="EmployeeTurnover")
        plt.xticks(rotation=35, ha="right")
        self._save(path, "Employee Turnover by Industry")

    def _innovation_score(self, data: pd.DataFrame, path: Path) -> None:
        summary = data.groupby("Industry", as_index=False)["ProductInnovation"].mean()
        plt.figure(figsize=(10, 6))
        sns.barplot(data=summary, x="Industry", y="ProductInnovation")
        plt.xticks(rotation=35, ha="right")
        self._save(path, "Average Innovation Score by Industry")

    def _correlation_heatmap(self, data: pd.DataFrame, path: Path) -> None:
        plt.figure(figsize=(12, 9))
        corr = data.select_dtypes("number").corr(numeric_only=True)
        sns.heatmap(corr, cmap="vlag", center=0, linewidths=0.4)
        self._save(path, "Correlation Heatmap")

    def _top_20_companies(self, data: pd.DataFrame, path: Path) -> None:
        top = data.nlargest(20, "BGPI")
        plt.figure(figsize=(11, 8))
        sns.barplot(data=top, y="CompanyName", x="BGPI", color="#4C78A8")
        self._save(path, "Top 20 Companies by BGPI")

    def _bottom_20_companies(self, data: pd.DataFrame, path: Path) -> None:
        bottom = data.nsmallest(20, "BGPI")
        plt.figure(figsize=(11, 8))
        sns.barplot(data=bottom, y="CompanyName", x="BGPI", color="#F58518")
        self._save(path, "Bottom 20 Companies by BGPI")
