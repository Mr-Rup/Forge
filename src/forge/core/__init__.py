"""Forge core framework machinery."""

from forge.core.discovery import (
    BasePluginDiscoverer,
    DirectoryPluginDiscoverer,
    DiscoveredPlugin,
    ModulePluginDiscoverer,
)
from forge.core.lifecycle import PluginLifecycleManager
from forge.core.loader import PluginLoader
from forge.core.registry import PluginRegistry
from forge.core.validator import PluginValidator, ValidationResult

__all__ = [
    "PluginLifecycleManager",
    "PluginRegistry",
    "PluginLoader",
    "PluginValidator",
    "ValidationResult",
    "DiscoveredPlugin",
    "BasePluginDiscoverer",
    "ModulePluginDiscoverer",
    "DirectoryPluginDiscoverer",
]
