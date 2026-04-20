"""
Utility functions for dictionary operations
"""

import re


def to_snakecase(name: str) -> str:
    """
    Transform camel case string to snake case string

    Args:
        name: String in camel case format

    Returns:
        String in snake case format
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def normalize_keys(data: dict) -> dict:
    """
    Recursively convert dictionary keys from camel case to snake case.

    Args:
        data: Dictionary to convert

    Returns:
        Dictionary with keys converted to snake case

    """
    if not isinstance(data, dict):
        return data

    return {to_snakecase(key): normalize_keys(value) for key, value in data.items()}
