"""Unit tests for the PluginRegistry."""

import pytest

from forge.contracts.plugin import Plugin, PluginMetadata
from forge.core.registry import PluginRegistry
from forge.exceptions.plugin import (
    PluginAlreadyRegisteredError,
    PluginNotFoundError,
)
from forge.plugins.hello import HelloPlugin

class MockPlugin(Plugin):
    """Auxiliary plugin for multi-plugin registry tests."""

    def __init__(self, name: str) -> None:
        super().__init__(
            PluginMetadata(
                name=name,
                version="1.0.0",
                description=f"Mock plugin {name}",
                author="Tester",
            )
        )

    def initialize(self) -> None:
        pass

    def execute(self) -> str:
        return self.metadata.name

    def shutdown(self) -> None:
        pass

def test_register_and_get_plugin() -> None:
    """Verify registering a plugin allows retrieval by name."""
    registry = PluginRegistry()
    plugin = HelloPlugin()

    registry.register(plugin)
    retrieved = registry.get("hello")

    assert retrieved is plugin
    assert retrieved.metadata.name == "hello"

def test_register_duplicate_raises_error() -> None:
    """Attempting to register a plugin with the same name must raise PluginAlreadyRegisteredError."""
    registry = PluginRegistry()
    plugin1 = HelloPlugin()
    plugin2 = HelloPlugin()

    registry.register(plugin1)
    with pytest.raises(PluginAlreadyRegisteredError, match="already registered"):
        registry.register(plugin2)

def test_get_nonexistent_plugin_raises_error() -> None:
    """Retrieving an unregistered plugin name must raise PluginNotFoundError."""
    registry = PluginRegistry()

    with pytest.raises(PluginNotFoundError, match="not registered"):
        registry.get("unknown")

def test_has_and_contains() -> None:
    """Verify membership checks using has() and 'in' operator."""
    registry = PluginRegistry()
    plugin = HelloPlugin()

    assert not registry.has("hello")
    assert "hello" not in registry

    registry.register(plugin)

    assert registry.has("hello")
    assert "hello" in registry
    assert "other" not in registry

def test_unregister_plugin() -> None:
    """Verify unregistering removes plugin from registry and returns it."""
    registry = PluginRegistry()
    plugin = HelloPlugin()

    registry.register(plugin)
    removed = registry.unregister("hello")

    assert removed is plugin
    assert not registry.has("hello")
    assert len(registry) == 0

def test_unregister_nonexistent_plugin_raises_error() -> None:
    """Unregistering an unregistered plugin must raise PluginNotFoundError."""
    registry = PluginRegistry()

    with pytest.raises(PluginNotFoundError, match="not registered"):
        registry.unregister("nonexistent")

def test_list_all_and_list_names() -> None:
    """Verify listing all plugin instances and their names."""
    registry = PluginRegistry()
    p1 = MockPlugin("p1")
    p2 = MockPlugin("p2")

    registry.register(p1)
    registry.register(p2)

    assert registry.list_names() == ["p1", "p2"]
    assert registry.list_all() == [p1, p2]

def test_len_and_iteration() -> None:
    """Verify length and iteration support."""
    registry = PluginRegistry()
    p1 = MockPlugin("alpha")
    p2 = MockPlugin("beta")

    registry.register(p1)
    registry.register(p2)

    assert len(registry) == 2
    assert list(registry) == [p1, p2]

def test_clear_registry() -> None:
    """Verify clear empties all registered plugins."""
    registry = PluginRegistry()
    registry.register(HelloPlugin())
    registry.register(MockPlugin("extra"))

    assert len(registry) == 2
    registry.clear()
    assert len(registry) == 0
    assert not registry.has("hello")
