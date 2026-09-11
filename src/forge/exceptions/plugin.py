"""Plugin-specific exceptions."""

from forge.exceptions.base import ForgeError


class PluginError(ForgeError):
    """Base exception for plugin-related failures."""


class InvalidStateTransitionError(PluginError):
    """Raised when an illegal lifecycle transition is attempted."""
