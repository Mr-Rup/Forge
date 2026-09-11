"""Unit tests for dynamic plugin loader."""

import pytest

from forge.contracts.plugin import Plugin, PluginMetadata, PluginState
from forge.core.discovery import DiscoveredPlugin
from forge.core.lifecycle import PluginLifecycleManager
from forge.core.loader import PluginLoader
from forge.core.registry import PluginRegistry
from forge.exceptions.plugin import PluginLoadError
from forge.plugins.hello import HelloPlugin

class BrokenInitPlugin(Plugin):
    """Plugin that fails during __init__."""

    def __init__(self) -> None:
        raise RuntimeError("Crash during __init__")

    def initialize(self) -> None:
        pass

    def execute(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

class ValidAuxPlugin(Plugin):
    """Valid auxiliary plugin for loader testing."""

    def __init__(self) -> None:
        super().__init__(
            PluginMetadata("aux", "1.0", "Auxiliary", "Tester")
        )

    def initialize(self) -> None:
        pass

    def execute(self) -> str:
        return "aux"

    def shutdown(self) -> None:
        pass

def test_load_discovered_plugin() -> None:
    """Verify loading a DiscoveredPlugin transitions it to LOADED."""
    candidate = DiscoveredPlugin(
        name="HelloPlugin",
        plugin_cls=HelloPlugin,
        source="forge.plugins.hello",
    )
    loader = PluginLoader()
    plugin = loader.load(candidate)

    assert isinstance(plugin, HelloPlugin)
    assert plugin.state == PluginState.LOADED

def test_load_plugin_class_directly() -> None:
    """Verify loading a Plugin class directly."""
    loader = PluginLoader()
    plugin = loader.load(HelloPlugin)

    assert isinstance(plugin, HelloPlugin)
    assert plugin.state == PluginState.LOADED

def test_load_registers_plugin_in_registry() -> None:
    """Verify loaded plugin is automatically registered in provided registry."""
    registry = PluginRegistry()
    loader = PluginLoader(registry=registry)

    plugin = loader.load(HelloPlugin)

    assert "hello" in registry
    assert registry.get("hello") is plugin

def test_load_invalid_candidate_raises_error() -> None:
    """Passing an invalid candidate type must raise PluginLoadError."""
    loader = PluginLoader()

    with pytest.raises(PluginLoadError, match="Expected DiscoveredPlugin"):
        loader.load("not_a_plugin")  # type: ignore[arg-type]

def test_load_instantiation_failure_raises_error() -> None:
    """Failing __init__ must raise PluginLoadError."""
    loader = PluginLoader()

    with pytest.raises(PluginLoadError, match="Failed to instantiate plugin"):
        loader.load(BrokenInitPlugin)

def test_load_all_happy_path() -> None:
    """Verify load_all loads multiple valid plugins."""
    registry = PluginRegistry()
    loader = PluginLoader(registry=registry)

    plugins = loader.load_all([HelloPlugin, ValidAuxPlugin])

    assert len(plugins) == 2
    assert "hello" in registry
    assert "aux" in registry

def test_load_all_failure_isolation() -> None:
    """With fail_fast=False, broken plugins are skipped without halting others."""
    registry = PluginRegistry()
    loader = PluginLoader(registry=registry)

    plugins = loader.load_all(
        [BrokenInitPlugin, HelloPlugin], fail_fast=False
    )

    assert len(plugins) == 1
    assert isinstance(plugins[0], HelloPlugin)
    assert "hello" in registry

def test_load_all_fail_fast_raises_error() -> None:
    """With fail_fast=True, broken plugin immediately raises PluginLoadError."""
    loader = PluginLoader()

    with pytest.raises(PluginLoadError):
        loader.load_all([BrokenInitPlugin, HelloPlugin], fail_fast=True)
