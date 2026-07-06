"""Report generation for PDF, Excel, and CSV outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config.config import AppConfig
from src.analysis import BusinessAnalyzer
from src.logger import get_logger


@dataclass
class ReportGenerator:
    """Create report files from scored company data."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)
        self.analyzer = BusinessAnalyzer(self.config)

    def generate(self, data: pd.DataFrame, chart_paths: list[Path] | None = None) -> dict[str, Path]:
        """Generate PDF, Excel, and CSV reports."""

        self.config.reports_dir.mkdir(parents=True, exist_ok=True)
        chart_paths = chart_paths or []
        outputs = {
            "csv": self._csv_report(data),
            "excel": self._excel_report(data),
            "pdf": self._pdf_report(data, chart_paths),
        }
        self.logger.info("Generated report files: %s.", outputs)
        return outputs

    def recommendations(self, data: pd.DataFrame) -> list[str]:
        """Generate concise business recommendations from aggregate signals."""

        average_bgpi = data["BGPI"].mean()
        average_turnover = data["EmployeeTurnover"].mean()
        average_margin = data["ProfitMargin"].mean()
        recommendations = []
        if average_bgpi < 55:
            recommendations.append("Prioritize margin improvement and customer retention before aggressive expansion.")
        else:
            recommendations.append("Scale high-BGPI segments with disciplined marketing allocation.")
        if average_turnover > 18:
            recommendations.append("Reduce employee turnover through retention programs and manager enablement.")
        if average_margin < 15:
            recommendations.append("Review operating expenses and pricing strategy for low-margin companies.")
        recommendations.append("Use industry-specific benchmarks when setting quarterly growth targets.")
        return recommendations

    def _csv_report(self, data: pd.DataFrame) -> Path:
        path = self.config.reports_dir / "business_growth_report.csv"
        data.sort_values("BGPI", ascending=False).to_csv(path, index=False)
        return path

    def _excel_report(self, data: pd.DataFrame) -> Path:
        path = self.config.reports_dir / "business_growth_report.xlsx"
        with pd.ExcelWriter(path) as writer:
            data.sort_values("BGPI", ascending=False).to_excel(writer, sheet_name="BGPI Rankings", index=False)
            self.analyzer.industry_summary(data).to_excel(writer, sheet_name="Industry Summary", index=False)
            self.analyzer.descriptive_statistics(data).to_excel(writer, sheet_name="Descriptive Stats")
            self.analyzer.correlation_matrix(data).to_excel(writer, sheet_name="Correlation Matrix")
            self.analyzer.profitability_analysis(data).head(100).to_excel(writer, sheet_name="Profitability", index=False)
        return path

    def _pdf_report(self, data: pd.DataFrame, chart_paths: list[Path]) -> Path:
        path = self.config.reports_dir / "business_growth_report.pdf"
        try:
            from fpdf import FPDF
        except ImportError:
            fallback = path.with_suffix(".txt")
            fallback.write_text(self._plain_report(data), encoding="utf-8")
            self.logger.warning("fpdf is unavailable; wrote text report to %s.", fallback)
            return fallback

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Business Growth Opportunity Analyzer", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, self._plain_report(data))

        for chart_path in chart_paths[:6]:
            if chart_path.exists():
                pdf.add_page()
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, chart_path.stem.replace("_", " ").title(), ln=True)
                pdf.image(str(chart_path), x=10, y=25, w=190)

        pdf.output(str(path))
        return path

    def _plain_report(self, data: pd.DataFrame) -> str:
        top = data.nlargest(5, "BGPI")[["CompanyName", "Industry", "BGPI"]]
        lines = [
            "Executive Summary",
            f"Companies analyzed: {len(data):,}",
            f"Average BGPI: {data['BGPI'].mean():.2f}",
            f"Average profit margin: {data['ProfitMargin'].mean():.2f}%",
            f"Average revenue growth: {data['RevenueGrowth'].mean():.2f}%",
            "",
            "Top Companies",
        ]
        lines.extend(
            f"- {row.CompanyName} ({row.Industry}): BGPI {row.BGPI:.2f}"
            for row in top.itertuples()
        )
        lines.append("")
        lines.append("Recommendations")
        lines.extend(f"- {item}" for item in self.recommendations(data))
        return "\n".join(lines)
