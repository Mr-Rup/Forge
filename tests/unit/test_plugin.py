"""Unit tests for plugin contracts and implementations."""

from dataclasses import FrozenInstanceError

import pytest

from forge.contracts.plugin import Plugin, PluginMetadata, PluginState
from forge.plugins.hello import HelloPlugin


def test_plugin_metadata() -> None:
    """Verify metadata attributes on HelloPlugin."""
    plugin = HelloPlugin()

    assert plugin.metadata.name == "hello"
    assert plugin.metadata.version == "1.0.0"
    assert plugin.metadata.description == "A simple demonstration plugin."
    assert plugin.metadata.author == "Rup"


def test_metadata_immutability() -> None:
    """Ensure PluginMetadata is frozen and cannot be modified."""
    meta = PluginMetadata("test", "0.1", "desc", "author")
    with pytest.raises(FrozenInstanceError):
        meta.name = "new_name"  # type: ignore[misc]


def test_plugin_initial_state() -> None:
    """Ensure a new plugin starts in DISCOVERED state."""
    plugin = HelloPlugin()
    assert plugin.state == PluginState.DISCOVERED


def test_plugin_execution() -> None:
    """Verify HelloPlugin execute returns expected message."""
    plugin = HelloPlugin()
    assert plugin.execute() == "Hello from Forge!"


def test_incomplete_plugin_cannot_be_instantiated() -> None:
    """Subclass without abstract methods should raise TypeError."""
    class BrokenPlugin(Plugin):
        pass

    with pytest.raises(TypeError):
        BrokenPlugin()  # type: ignore[abstract]
