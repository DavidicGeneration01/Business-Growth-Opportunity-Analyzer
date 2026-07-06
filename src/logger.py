"""Logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path

from config.config import AppConfig


def get_logger(name: str, config: AppConfig | None = None) -> logging.Logger:
    """Return a configured application logger."""

    cfg = config or AppConfig()
    cfg.ensure_directories()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_path: Path = cfg.logs_dir / "business_growth_analyzer.log"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
