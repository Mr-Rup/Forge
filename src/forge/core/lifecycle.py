"""Plugin lifecycle coordinator and transition rules."""

from typing import Dict, Set

from forge.contracts.plugin import Plugin, PluginState
from forge.exceptions.plugin import InvalidStateTransitionError

# Valid state progression map
VALID_TRANSITIONS: Dict[PluginState, Set[PluginState]] = {
    PluginState.DISCOVERED: {
        PluginState.LOADED,
        PluginState.FAILED,
    },
    PluginState.LOADED: {
        PluginState.INITIALIZED,
        PluginState.FAILED,
    },
    PluginState.INITIALIZED: {
        PluginState.ACTIVE,
        PluginState.STOPPED,
        PluginState.FAILED,
    },
    PluginState.ACTIVE: {
        PluginState.STOPPED,
        PluginState.FAILED,
    },
    PluginState.STOPPED: {
        PluginState.INITIALIZED,
        PluginState.LOADED,
    },
    PluginState.FAILED: set(),
}


class PluginLifecycleManager:
    """Manages state transitions and lifecycle methods for plugins."""

    def load(self, plugin: Plugin) -> None:
        """Mark plugin as loaded into the system."""
        self._transition(plugin, PluginState.LOADED)

    def initialize(self, plugin: Plugin) -> None:
        """Initialize plugin and transition to INITIALIZED (or FAILED on error)."""
        try:
            plugin.initialize()
            self._transition(plugin, PluginState.INITIALIZED)
        except Exception:
            self._transition(plugin, PluginState.FAILED)
            raise

    def activate(self, plugin: Plugin) -> None:
        """Transition initialized plugin to ACTIVE state."""
        self._transition(plugin, PluginState.ACTIVE)

    def stop(self, plugin: Plugin) -> None:
        """Shut down plugin and transition to STOPPED (or FAILED on error)."""
        try:
            plugin.shutdown()
            self._transition(plugin, PluginState.STOPPED)
        except Exception:
            self._transition(plugin, PluginState.FAILED)
            raise

    def _transition(self, plugin: Plugin, new_state: PluginState) -> None:
        """Validate and apply state transition."""
        allowed_states = VALID_TRANSITIONS.get(plugin.state, set())

        if new_state not in allowed_states:
            raise InvalidStateTransitionError(
                f"Cannot transition plugin '{plugin.metadata.name}' "
                f"from {plugin.state.name} to {new_state.name}"
            )

        plugin.state = new_state
