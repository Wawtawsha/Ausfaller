"""
Shared utility functions for the social-scraper pipeline.

Provides type coercion and dataclass serialization utilities.
"""

from dataclasses import fields
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int, returning default if not possible.

    Args:
        value: Value to convert (int, float, str, or other)
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default if not possible.

    Args:
        value: Value to convert (int, float, str, or other)
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def dataclass_to_dict(obj: Any) -> Any:
    """Recursively convert a dataclass instance to a dictionary.

    Handles:
    - Nested dataclasses
    - Lists and dicts containing dataclasses
    - Enum values (converts to .value)
    - datetime objects (converts to ISO format string)
    - Path objects (converts to string)

    Args:
        obj: Object to convert (dataclass, list, dict, or primitive)

    Returns:
        Dictionary representation or primitive value
    """
    if hasattr(obj, "__dataclass_fields__"):
        return {k: dataclass_to_dict(v) for k, v in obj.__dict__.items()}
    if isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return obj
