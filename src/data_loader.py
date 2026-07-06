"""Dataset loading and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config.config import AppConfig
from src.logger import get_logger


@dataclass
class DataLoader:
    """Load and validate CSV datasets."""

    config: AppConfig = field(default_factory=AppConfig)

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__, self.config)

    def load(self, path: Path | None = None) -> pd.DataFrame:
        """Load a CSV file and validate its schema."""

        input_path = path or self.config.raw_dataset_path
        if not input_path.exists():
            raise FileNotFoundError(f"Dataset not found: {input_path}")

        try:
            data = pd.read_csv(input_path)
        except pd.errors.ParserError as exc:
            self.logger.exception("Failed to parse dataset: %s", input_path)
            raise ValueError(f"Invalid CSV format: {input_path}") from exc

        missing = set(self.config.required_columns).difference(data.columns)
        if missing:
            raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

        self.logger.info("Loaded dataset with shape %s from %s.", data.shape, input_path)
        return data
