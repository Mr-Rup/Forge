"""Plugin registry for tracking registered plugins."""

from typing import Iterator, List

from forge.contracts.plugin import Plugin
from forge.exceptions.plugin import (
    PluginAlreadyRegisteredError,
    PluginNotFoundError,
)

class PluginRegistry:
    """Maintains a collection of known plugins without knowing their internal details."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance by its metadata name."""
        name = plugin.metadata.name
        if name in self._plugins:
            raise PluginAlreadyRegisteredError(
                f"Plugin '{name}' is already registered."
            )
        self._plugins[name] = plugin

    def unregister(self, name: str) -> Plugin:
        """Remove and return a registered plugin by name."""
        if name not in self._plugins:
            raise PluginNotFoundError(
                f"Plugin '{name}' is not registered."
            )
        return self._plugins.pop(name)

    def get(self, name: str) -> Plugin:
        """Retrieve a registered plugin by name."""
        if name not in self._plugins:
            raise PluginNotFoundError(
                f"Plugin '{name}' is not registered."
            )
        return self._plugins[name]

    def has(self, name: str) -> bool:
        """Check whether a plugin with the given name exists."""
        return name in self._plugins

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for checking plugin registration."""
        return self.has(name)

    def list_all(self) -> List[Plugin]:
        """Return a list of all registered plugin instances."""
        return list(self._plugins.values())

    def list_names(self) -> List[str]:
        """Return a list of names of all registered plugins."""
        return list(self._plugins.keys())

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()

    def __len__(self) -> int:
        """Return the number of registered plugins."""
        return len(self._plugins)

    def __iter__(self) -> Iterator[Plugin]:
        """Iterate over all registered plugins."""
        return iter(self._plugins.values())
