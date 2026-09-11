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


class PluginDiscoveryError(PluginError):
    """Raised when an error occurs during plugin discovery."""


class PluginLoadError(PluginError):
    """Raised when an error occurs while importing or instantiating a plugin."""


class PluginValidationError(PluginError):
    """Raised when a plugin fails specification or contract validation."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


class PluginInitializationError(PluginError):
    """Raised when a plugin crashes during initialization."""


class PluginExecutionError(PluginError):
    """Raised when a plugin crashes during execution."""


class PluginShutdownError(PluginError):
    """Raised when a plugin crashes during shutdown."""
