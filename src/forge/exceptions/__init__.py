"""Forge exceptions."""

from forge.exceptions.base import ForgeError
from forge.exceptions.configuration import ConfigurationError
from forge.exceptions.plugin import (
    InvalidStateTransitionError,
    PluginAlreadyRegisteredError,
    PluginDiscoveryError,
    PluginError,
    PluginExecutionError,
    PluginInitializationError,
    PluginLoadError,
    PluginNotFoundError,
    PluginShutdownError,
    PluginValidationError,
)

__all__ = [
    "ForgeError",
    "ConfigurationError",
    "PluginError",
    "InvalidStateTransitionError",
    "PluginAlreadyRegisteredError",
    "PluginNotFoundError",
    "PluginDiscoveryError",
    "PluginLoadError",
    "PluginValidationError",
    "PluginInitializationError",
    "PluginExecutionError",
    "PluginShutdownError",
]
