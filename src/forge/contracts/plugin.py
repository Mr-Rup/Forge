from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class PluginState(Enum):
    """Lifecycle states of a plugin."""
    DISCOVERED = auto()
    LOADED = auto()
    INITIALIZED = auto()
    ACTIVE = auto()
    STOPPED = auto()
    FAILED = auto()


@dataclass(frozen=True)
class PluginMetadata:
    """Immutable metadata describing a plugin."""
    name: str
    version: str
    description: str
    author: str


class Plugin(ABC):
    """Abstract base contract that all Forge plugins must implement."""

    def __init__(self, metadata: PluginMetadata) -> None:
        self.metadata = metadata
        self.state: PluginState = PluginState.DISCOVERED

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin resources."""
        pass

    @abstractmethod
    def execute(self) -> Any:
        """Execute core plugin logic."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources upon shutdown."""
        pass
