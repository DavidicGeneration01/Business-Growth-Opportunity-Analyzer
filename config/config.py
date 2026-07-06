"""Application configuration for the Business Growth Opportunity Analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    """Centralized paths and application constants."""

    random_seed: int = 42
    dataset_size: int = 5000
    base_dir: Path = BASE_DIR
    assets_dir: Path = BASE_DIR / "assets"
    data_dir: Path = BASE_DIR / "data"
    raw_dir: Path = BASE_DIR / "data" / "raw"
    processed_dir: Path = BASE_DIR / "data" / "processed"
    exports_dir: Path = BASE_DIR / "data" / "exports"
    reports_dir: Path = BASE_DIR / "reports"
    charts_dir: Path = BASE_DIR / "reports" / "charts"
    logs_dir: Path = BASE_DIR / "logs"
    raw_dataset_path: Path = BASE_DIR / "data" / "raw" / "businesses_raw.csv"
    cleaned_dataset_path: Path = BASE_DIR / "data" / "processed" / "businesses_clean.csv"
    bgpi_scores_path: Path = BASE_DIR / "data" / "processed" / "bgpi_scores.csv"
    industry_summary_path: Path = BASE_DIR / "data" / "processed" / "industry_summary.csv"
    company_summary_path: Path = BASE_DIR / "data" / "processed" / "company_summary.csv"
    growth_report_path: Path = BASE_DIR / "data" / "processed" / "growth_report.csv"
    industries: tuple[str, ...] = (
        "Technology",
        "Retail",
        "Healthcare",
        "Manufacturing",
        "Finance",
        "Education",
        "Logistics",
        "Energy",
        "Hospitality",
        "Real Estate",
    )
    countries: tuple[str, ...] = (
        "United States",
        "Canada",
        "United Kingdom",
        "Germany",
        "France",
        "Nigeria",
        "South Africa",
        "India",
        "Brazil",
        "Australia",
    )
    required_columns: tuple[str, ...] = (
        "CompanyID",
        "CompanyName",
        "Industry",
        "Country",
        "YearsOperating",
        "Employees",
        "MonthlyRevenue",
        "MonthlyExpenses",
        "MarketingBudget",
        "NewCustomers",
        "RepeatCustomers",
        "CustomerSatisfaction",
        "EmployeeTurnover",
        "ProductInnovation",
        "MarketShare",
        "RevenueGrowth",
        "ProfitMargin",
    )
    numeric_ranges: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {
            "YearsOperating": (0, 150),
            "Employees": (1, 250000),
            "MonthlyRevenue": (0, 1_000_000_000),
            "MonthlyExpenses": (0, 1_000_000_000),
            "MarketingBudget": (0, 200_000_000),
            "NewCustomers": (0, 5_000_000),
            "RepeatCustomers": (0, 5_000_000),
            "CustomerSatisfaction": (1, 10),
            "EmployeeTurnover": (0, 100),
            "ProductInnovation": (1, 10),
            "MarketShare": (0, 100),
            "RevenueGrowth": (-100, 300),
            "ProfitMargin": (-100, 100),
        }
    )

    def ensure_directories(self) -> None:
        """Create all runtime output directories."""

        for directory in (
            self.assets_dir,
            self.raw_dir,
            self.processed_dir,
            self.exports_dir,
            self.reports_dir,
            self.charts_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
