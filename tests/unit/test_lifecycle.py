"""Unit tests for plugin lifecycle management and state transitions."""

import pytest

from forge.contracts.plugin import Plugin, PluginMetadata, PluginState
from forge.core.lifecycle import PluginLifecycleManager
from forge.exceptions.plugin import (
    InvalidStateTransitionError,
    PluginInitializationError,
    PluginShutdownError,
)
from forge.plugins.hello import HelloPlugin

def test_plugin_happy_path_lifecycle() -> None:
    """Verify complete valid lifecycle progression."""
    plugin = HelloPlugin()
    manager = PluginLifecycleManager()

    assert plugin.state == PluginState.DISCOVERED

    manager.load(plugin)
    assert plugin.state == PluginState.LOADED

    manager.initialize(plugin)
    assert plugin.state == PluginState.INITIALIZED

    manager.activate(plugin)
    assert plugin.state == PluginState.ACTIVE

    manager.stop(plugin)
    assert plugin.state == PluginState.STOPPED

def test_invalid_state_transition_raises_error() -> None:
    """Transitioning out of order must raise InvalidStateTransitionError."""
    plugin = HelloPlugin()
    manager = PluginLifecycleManager()

    # Attempting to activate a discovered plugin directly
    with pytest.raises(InvalidStateTransitionError):
        manager.activate(plugin)

def test_initialization_failure_transitions_to_failed() -> None:
    """Failing during initialize must transition plugin to FAILED and raise PluginInitializationError."""
    class FaultyInitPlugin(Plugin):
        def initialize(self) -> None:
            raise RuntimeError("Init crashed")

        def execute(self) -> None:
            pass

        def shutdown(self) -> None:
            pass

    plugin = FaultyInitPlugin(
        PluginMetadata("faulty", "1.0", "Fails on init", "Rup")
    )
    manager = PluginLifecycleManager()
    manager.load(plugin)

    with pytest.raises(PluginInitializationError, match="failed during initialization"):
        manager.initialize(plugin)

    assert plugin.state == PluginState.FAILED

def test_shutdown_failure_transitions_to_failed() -> None:
    """Failing during shutdown must transition plugin to FAILED and raise PluginShutdownError."""
    class FaultyShutdownPlugin(Plugin):
        def initialize(self) -> None:
            pass

        def execute(self) -> None:
            pass

        def shutdown(self) -> None:
            raise RuntimeError("Shutdown crashed")

    plugin = FaultyShutdownPlugin(
        PluginMetadata("faulty", "1.0", "Fails on shutdown", "Rup")
    )
    manager = PluginLifecycleManager()
    manager.load(plugin)
    manager.initialize(plugin)
    manager.activate(plugin)

    with pytest.raises(PluginShutdownError, match="failed during shutdown"):
        manager.stop(plugin)

    assert plugin.state == PluginState.FAILED