"""Configuration-specific exceptions."""

from forge.exceptions.base import ForgeError


class ConfigurationError(ForgeError):
    """Base exception for framework configuration errors."""
