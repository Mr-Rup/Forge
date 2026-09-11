"""Plugin-specific exceptions."""

from forge.exceptions.base import ForgeError


class PluginError(ForgeError):
    """Base exception for plugin-related failures."""


class InvalidStateTransitionError(PluginError):
    """Raised when an illegal lifecycle transition is attempted."""


class PluginAlreadyRegisteredError(PluginError):
    """Raised when attempting to register a plugin name that is already present."""


class PluginNotFoundError(PluginError):
    """Raised when an expected plugin is not found in the registry."""
