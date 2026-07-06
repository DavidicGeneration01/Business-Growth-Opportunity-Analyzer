"""Generate realistic fictional business data."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from random import Random

import numpy as np
import pandas as pd

from config.config import AppConfig
from src.logger import get_logger
from src.utils import ensure_parent


@dataclass
class DatasetGenerator:
    """Create a synthetic company dataset."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)
        self.random = Random(self.config.random_seed)
        self.rng = np.random.default_rng(self.config.random_seed)

    def generate(self, rows: int | None = None) -> pd.DataFrame:
        """Generate fictional companies as a Pandas DataFrame."""

        count = rows or self.config.dataset_size
        if not 1000 <= count <= 5000:
            raise ValueError("Dataset size must be between 1,000 and 5,000 rows.")

        records: list[dict[str, object]] = []
        industry_profiles = self._industry_profiles()
        prefixes = ["Apex", "Nova", "Bright", "Vertex", "Summit", "Blue", "Prime"]
        suffixes = ["Labs", "Works", "Group", "Systems", "Ventures", "Holdings", "Dynamics"]

        for index in range(1, count + 1):
            industry = self.random.choice(self.config.industries)
            profile = industry_profiles[industry]
            country = self.random.choice(self.config.countries)
            years = int(self.rng.integers(1, 45))
            employees = int(max(5, self.rng.lognormal(profile["employee_mu"], 0.85)))
            monthly_revenue = float(
                max(10_000, self.rng.lognormal(profile["revenue_mu"], 0.75))
            )
            expense_ratio = float(self.rng.normal(profile["expense_ratio"], 0.09))
            monthly_expenses = monthly_revenue * np.clip(expense_ratio, 0.35, 1.25)
            marketing_budget = monthly_revenue * float(self.rng.uniform(0.015, 0.14))
            customer_base = max(1, int(monthly_revenue / self.rng.uniform(150, 2500)))
            new_customers = int(max(0, self.rng.normal(customer_base * 0.18, customer_base * 0.06)))
            repeat_customers = int(max(0, self.rng.normal(customer_base * 0.42, customer_base * 0.12)))
            satisfaction = float(np.clip(self.rng.normal(profile["satisfaction"], 1.0), 1, 10))
            turnover = float(np.clip(self.rng.normal(profile["turnover"], 6), 1, 60))
            innovation = float(np.clip(self.rng.normal(profile["innovation"], 1.2), 1, 10))
            market_share = float(np.clip(self.rng.beta(1.8, 12) * 100, 0.1, 45))
            profit_margin = ((monthly_revenue - monthly_expenses) / monthly_revenue) * 100
            revenue_growth = float(
                np.clip(
                    self.rng.normal(profile["growth"], 12)
                    + (innovation - 5) * 2
                    + (satisfaction - 5),
                    -45,
                    95,
                )
            )

            records.append(
                {
                    "CompanyID": f"BG-{index:05d}",
                    "CompanyName": f"{self.random.choice(prefixes)} {self._name_seed()} {self.random.choice(suffixes)}",
                    "Industry": industry,
                    "Country": country,
                    "YearsOperating": years,
                    "Employees": employees,
                    "MonthlyRevenue": round(monthly_revenue, 2),
                    "MonthlyExpenses": round(monthly_expenses, 2),
                    "MarketingBudget": round(marketing_budget, 2),
                    "NewCustomers": new_customers,
                    "RepeatCustomers": repeat_customers,
                    "CustomerSatisfaction": round(satisfaction, 2),
                    "EmployeeTurnover": round(turnover, 2),
                    "ProductInnovation": round(innovation, 2),
                    "MarketShare": round(market_share, 2),
                    "RevenueGrowth": round(revenue_growth, 2),
                    "ProfitMargin": round(profit_margin, 2),
                }
            )

        data = pd.DataFrame.from_records(records)
        self.logger.info("Generated %s fictional company records.", len(data))
        return data

    def save(self, path: Path | None = None, rows: int | None = None) -> Path:
        """Generate and save the dataset to CSV."""

        output_path = path or self.config.raw_dataset_path
        ensure_parent(output_path)
        self.generate(rows).to_csv(output_path, index=False)
        self.logger.info("Saved raw dataset to %s.", output_path)
        return output_path

    def _name_seed(self) -> str:
        syllables = ["cor", "zen", "via", "lum", "tek", "ora", "fin", "med", "sol", "mar"]
        return f"{self.random.choice(syllables)}{self.random.choice(syllables)}".title()

    @staticmethod
    def _industry_profiles() -> dict[str, dict[str, float]]:
        return {
            "Technology": {"employee_mu": 5.1, "revenue_mu": 12.9, "expense_ratio": 0.68, "growth": 24, "innovation": 8.0, "satisfaction": 7.8, "turnover": 14},
            "Retail": {"employee_mu": 5.6, "revenue_mu": 12.4, "expense_ratio": 0.78, "growth": 12, "innovation": 5.5, "satisfaction": 7.0, "turnover": 22},
            "Healthcare": {"employee_mu": 5.4, "revenue_mu": 12.7, "expense_ratio": 0.72, "growth": 15, "innovation": 6.5, "satisfaction": 8.1, "turnover": 12},
            "Manufacturing": {"employee_mu": 6.0, "revenue_mu": 13.1, "expense_ratio": 0.76, "growth": 10, "innovation": 5.9, "satisfaction": 6.9, "turnover": 16},
            "Finance": {"employee_mu": 5.0, "revenue_mu": 13.0, "expense_ratio": 0.64, "growth": 14, "innovation": 6.7, "satisfaction": 7.4, "turnover": 13},
            "Education": {"employee_mu": 4.7, "revenue_mu": 11.9, "expense_ratio": 0.74, "growth": 11, "innovation": 6.2, "satisfaction": 7.6, "turnover": 15},
            "Logistics": {"employee_mu": 5.8, "revenue_mu": 12.6, "expense_ratio": 0.80, "growth": 13, "innovation": 5.7, "satisfaction": 6.8, "turnover": 19},
            "Energy": {"employee_mu": 5.7, "revenue_mu": 13.2, "expense_ratio": 0.70, "growth": 9, "innovation": 6.1, "satisfaction": 7.1, "turnover": 11},
            "Hospitality": {"employee_mu": 5.3, "revenue_mu": 12.0, "expense_ratio": 0.82, "growth": 8, "innovation": 5.2, "satisfaction": 7.2, "turnover": 28},
            "Real Estate": {"employee_mu": 4.8, "revenue_mu": 12.8, "expense_ratio": 0.66, "growth": 12, "innovation": 5.8, "satisfaction": 7.3, "turnover": 12},
        }
