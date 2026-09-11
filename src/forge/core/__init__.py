"""Forge core framework machinery."""

from forge.core.discovery import (
    BasePluginDiscoverer,
    DirectoryPluginDiscoverer,
    DiscoveredPlugin,
    ModulePluginDiscoverer,
)
from forge.core.lifecycle import PluginLifecycleManager
from forge.core.registry import PluginRegistry

__all__ = [
    "PluginLifecycleManager",
    "PluginRegistry",
    "DiscoveredPlugin",
    "BasePluginDiscoverer",
    "ModulePluginDiscoverer",
    "DirectoryPluginDiscoverer",
]
