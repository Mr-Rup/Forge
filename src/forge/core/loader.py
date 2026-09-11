"""Dynamic plugin loader for instantiating and loading plugin candidates."""

from typing import Iterable, List, Optional, Union

from forge.contracts.plugin import Plugin
from forge.core.discovery import DiscoveredPlugin
from forge.core.lifecycle import PluginLifecycleManager
from forge.core.registry import PluginRegistry
from forge.core.validator import PluginValidator
from forge.exceptions.plugin import PluginLoadError


class PluginLoader:
    """Instantiates plugins and coordinates their initial loading and registration."""

    def __init__(
        self,
        lifecycle_manager: Optional[PluginLifecycleManager] = None,
        registry: Optional[PluginRegistry] = None,
        validator: Optional[PluginValidator] = None,
    ) -> None:
        self.lifecycle_manager = lifecycle_manager or PluginLifecycleManager()
        self.registry = registry
        self.validator = validator or PluginValidator()

    def load(
        self, candidate: Union[DiscoveredPlugin, type[Plugin]]
    ) -> Plugin:
        """Instantiate a plugin candidate and transition it to LOADED state."""
        plugin_cls: type[Plugin]
        source_desc: str

        if isinstance(candidate, DiscoveredPlugin):
            plugin_cls = candidate.plugin_cls
            source_desc = f"'{candidate.name}' from {candidate.source}"
        elif isinstance(candidate, type) and issubclass(candidate, Plugin):
            plugin_cls = candidate
            source_desc = f"class '{candidate.__name__}'"
        else:
            raise PluginLoadError(
                f"Expected DiscoveredPlugin or Plugin subclass, got {type(candidate).__name__}"
            )

        try:
            plugin = plugin_cls()
        except Exception as e:
            raise PluginLoadError(
                f"Failed to instantiate plugin {source_desc}: {e}"
            ) from e

        # Validate plugin specification
        if self.validator is not None:
            self.validator.validate(plugin)

        # Transition to LOADED state
        self.lifecycle_manager.load(plugin)

        # Register plugin if registry is configured
        if self.registry is not None:
            self.registry.register(plugin)

        return plugin

    def load_all(
        self,
        candidates: Iterable[Union[DiscoveredPlugin, type[Plugin]]],
        fail_fast: bool = True,
    ) -> List[Plugin]:
        """Load multiple plugin candidates with optional failure isolation."""
        loaded: List[Plugin] = []

        for candidate in candidates:
            try:
                plugin = self.load(candidate)
                loaded.append(plugin)
            except Exception:
                if fail_fast:
                    raise
                continue

        return loaded
