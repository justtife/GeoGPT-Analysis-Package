import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json


class GeoGPTLogger:
    """
    A professional logging setup for the geospatial package.

    Features:
    - Console and file logging
    - JSON logging for production
    - Configurable log levels
    - Rotating file handler
    - Structured logging for better analysis
    """

    _initialized = False

    @classmethod
    def initialize(
        cls,
        log_level: str = "INFO",
        log_file: Optional[Path] = None,
        json_logging: bool = False,
        log_format: Optional[str] = None
    ) -> None:
        """
        Initialize the package logger.

        Args:
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (optional)
            json_logging: Whether to use JSON formatted logs
            log_format: Custom log format string
        """
        if cls._initialized:
            return

        logger = logging.getLogger("geogpt")
        logger.setLevel(log_level.upper())

        # Prevent adding multiple handlers if initialized multiple times
        if logger.handlers:
            return

        # Default console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Configure formatters
        if json_logging:
            formatter = cls._get_json_formatter()
        else:
            formatter = logging.Formatter(
                log_format or cls._get_default_formatter(),
                datefmt="%Y-%m-%d %H:%M:%S"
            )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Add file handler if log file specified
        if log_file:
            file_handler = cls._get_file_handler(log_file, formatter)
            logger.addHandler(file_handler)

        cls._initialized = True

    @staticmethod
    def _get_default_formatter() -> str:
        """Return default log format string."""
        return (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(lineno)d - %(message)s"
        )

    @staticmethod
    def _get_json_formatter() -> logging.Formatter:
        """Return JSON formatter for structured logging."""
        from pythonjsonlogger import jsonlogger

        return jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(module)s %(lineno)d %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "name": "logger",
                "levelname": "level",
                "module": "module",
                "lineno": "line_number",
                "message": "message"
            }
        )

    @staticmethod
    def _get_file_handler(
        log_file: Path,
        formatter: logging.Formatter
    ) -> logging.Handler:
        """Create and configure a rotating file handler."""
        from logging.handlers import RotatingFileHandler

        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        handler.setFormatter(formatter)
        return handler

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance for the specified name.

        Args:
            name: Logger name (defaults to package root logger)

        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.initialize()
        return logging.getLogger(name or "geogpt")
