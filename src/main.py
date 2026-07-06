"""Main orchestration script for the complete workflow."""

from __future__ import annotations

from config.config import AppConfig
from src.analysis import BusinessAnalyzer
from src.bgpi import BGPICalculator
from src.cleaner import DataCleaner
from src.data_loader import DataLoader
from src.dataset_generator import DatasetGenerator
from src.logger import get_logger
from src.report_generator import ReportGenerator
from src.visualization import BusinessVisualizer


def run_pipeline(config: AppConfig | None = None) -> dict[str, object]:
    """Run generation, cleaning, scoring, analysis, visualization, and reports."""

    cfg = config or AppConfig()
    cfg.ensure_directories()
    logger = get_logger("Main", cfg)
    logger.info("Starting Business Growth Opportunity Analyzer workflow.")

    raw_path = DatasetGenerator(cfg).save(rows=cfg.dataset_size)
    raw_data = DataLoader(cfg).load(raw_path)

    cleaner = DataCleaner(cfg)
    cleaned_data = cleaner.clean(raw_data)
    cleaned_path = cleaner.export(cleaned_data)

    bgpi = BGPICalculator(cfg)
    scored_data = bgpi.calculate(cleaned_data)
    bgpi_path = bgpi.export(scored_data)

    analyzer = BusinessAnalyzer(cfg)
    analysis_paths = analyzer.export_outputs(scored_data)

    chart_paths = BusinessVisualizer(cfg).generate_all(scored_data)
    report_paths = ReportGenerator(cfg).generate(scored_data, chart_paths)

    logger.info("Workflow completed successfully.")
    return {
        "raw_dataset": raw_path,
        "cleaned_dataset": cleaned_path,
        "bgpi_scores": bgpi_path,
        "analysis_outputs": analysis_paths,
        "charts": chart_paths,
        "reports": report_paths,
    }


if __name__ == "__main__":
    run_pipeline()
