"""Plugin discovery strategies for finding available plugins."""

import importlib, importlib.util, inspect, pkgutil, sys

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, List, Union

from forge.contracts.plugin import Plugin
from forge.exceptions.plugin import PluginDiscoveryError

@dataclass(frozen=True)
class DiscoveredPlugin:
    """Represents a discovered plugin candidate."""

    name: str
    plugin_cls: type[Plugin]
    source: str

def is_plugin_subclass(obj: Any) -> bool:
    """Check if an object is a concrete Plugin subclass."""
    return (
        isinstance(obj, type)
        and issubclass(obj, Plugin)
        and obj is not Plugin
        and not inspect.isabstract(obj)
    )

class BasePluginDiscoverer(ABC):
    """Abstract base class for plugin discovery mechanisms."""

    @abstractmethod
    def discover(self) -> List[DiscoveredPlugin]:
        """Discover and return available plugin candidates."""
        pass

class ModulePluginDiscoverer(BasePluginDiscoverer):
    """Discovers plugins inside a Python module or package."""

    def __init__(self, target: Union[str, ModuleType]) -> None:
        self.target = target

    def discover(self) -> List[DiscoveredPlugin]:
        """Scan target module and its submodules for Plugin subclasses."""
        if isinstance(self.target, str):
            try:
                module = importlib.import_module(self.target)
            except ImportError as e:
                raise PluginDiscoveryError(
                    f"Could not import module '{self.target}': {e}"
                ) from e
        else:
            module = self.target

        discovered: List[DiscoveredPlugin] = []

        # If target is a package, scan submodules
        if hasattr(module, "__path__"):
            for _, modname, _ in pkgutil.iter_modules(
                module.__path__, module.__name__ + "."
            ):
                try:
                    submod = importlib.import_module(modname)
                    discovered.extend(self._scan_module(submod))
                except ImportError as e:
                    raise PluginDiscoveryError(
                        f"Error importing submodule '{modname}': {e}"
                    ) from e

        # Scan the module/package itself
        discovered.extend(self._scan_module(module))

        # Deduplicate results by plugin class
        unique: dict[type[Plugin], DiscoveredPlugin] = {}
        for item in discovered:
            if item.plugin_cls not in unique:
                unique[item.plugin_cls] = item

        return list(unique.values())

    def _scan_module(self, module: ModuleType) -> List[DiscoveredPlugin]:
        """Extract concrete Plugin subclasses from a module."""
        results: List[DiscoveredPlugin] = []
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue
            attr = getattr(module, attr_name, None)
            if is_plugin_subclass(attr):
                results.append(
                    DiscoveredPlugin(
                        name=attr.__name__,
                        plugin_cls=attr,
                        source=module.__name__,
                    )
                )
        return results

class DirectoryPluginDiscoverer(BasePluginDiscoverer):
    """Discovers plugins by scanning Python files in a directory."""

    def __init__(self, directory: Union[str, Path]) -> None:
        self.directory = Path(directory)

    def discover(self) -> List[DiscoveredPlugin]:
        """Scan directory for .py files containing Plugin subclasses."""
        if not self.directory.exists() or not self.directory.is_dir():
            raise PluginDiscoveryError(
                f"Directory not found: '{self.directory}'"
            )

        discovered: List[DiscoveredPlugin] = []
        for py_file in sorted(self.directory.glob("*.py")):
            if py_file.name.startswith("_"):
                continue

            module_name = f"_forge_discovered_{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(
                    module_name, py_file
                )
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
            except Exception as e:
                raise PluginDiscoveryError(
                    f"Failed to load file '{py_file}': {e}"
                ) from e

            for attr_name in dir(mod):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(mod, attr_name, None)
                if is_plugin_subclass(attr):
                    discovered.append(
                        DiscoveredPlugin(
                            name=attr.__name__,
                            plugin_cls=attr,
                            source=str(py_file),
                        )
                    )

        return discovered
