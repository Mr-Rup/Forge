"""Unit tests for plugin discovery mechanisms."""

import pytest, sys
from types import ModuleType

from forge.contracts.plugin import Plugin, PluginMetadata
from forge.core.discovery import (
    DirectoryPluginDiscoverer,
    DiscoveredPlugin,
    ModulePluginDiscoverer,
)
from forge.exceptions.plugin import PluginDiscoveryError
from forge.plugins.hello import HelloPlugin

def test_module_discoverer_finds_hello_plugin() -> None:
    """Verify ModulePluginDiscoverer finds HelloPlugin in forge.plugins."""
    discoverer = ModulePluginDiscoverer("forge.plugins")
    plugins = discoverer.discover()

    assert len(plugins) == 1
    discovered = plugins[0]

    assert isinstance(discovered, DiscoveredPlugin)
    assert discovered.name == "HelloPlugin"
    assert discovered.plugin_cls is HelloPlugin
    assert discovered.source == "forge.plugins.hello"

def test_module_discoverer_ignores_abstract_and_non_plugins() -> None:
    """Verify discoverer filters out abstract subclasses and regular classes."""
    test_mod = ModuleType("dynamic_test_module")

    # Regular class
    class RegularClass:
        pass

    # Abstract Plugin subclass
    class AbstractCustomPlugin(Plugin):
        pass

    # Concrete Plugin subclass
    class ValidCustomPlugin(Plugin):
        def __init__(self) -> None:
            super().__init__(
                PluginMetadata("valid", "1.0", "Valid plugin", "Tester")
            )

        def initialize(self) -> None:
            pass

        def execute(self) -> str:
            return "ok"

        def shutdown(self) -> None:
            pass

    test_mod.RegularClass = RegularClass  # type: ignore[attr-defined]
    test_mod.AbstractCustomPlugin = AbstractCustomPlugin  # type: ignore[attr-defined]
    test_mod.ValidCustomPlugin = ValidCustomPlugin  # type: ignore[attr-defined]

    discoverer = ModulePluginDiscoverer(test_mod)
    results = discoverer.discover()

    assert len(results) == 1
    assert results[0].plugin_cls is ValidCustomPlugin

def test_module_discoverer_invalid_module_raises_error() -> None:
    """Importing a nonexistent module must raise PluginDiscoveryError."""
    discoverer = ModulePluginDiscoverer("nonexistent.module.for.sure")
    with pytest.raises(PluginDiscoveryError, match="Could not import module"):
        discoverer.discover()

def test_directory_discoverer_finds_plugins(tmp_path) -> None:
    """Verify DirectoryPluginDiscoverer finds plugins in a directory."""
    plugin_code = """
from forge.contracts.plugin import Plugin, PluginMetadata

class DynamicPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__(PluginMetadata("dyn", "1.0", "Dynamic", "Test"))

    def initialize(self) -> None:
        pass

    def execute(self) -> str:
        return "dynamic"

    def shutdown(self) -> None:
        pass
"""
    plugin_file = tmp_path / "sample_plugin.py"
    plugin_file.write_text(plugin_code, encoding="utf-8")

    # Also write a non-plugin file
    helper_file = tmp_path / "helper.py"
    helper_file.write_text("SOME_VAR = 42\n", encoding="utf-8")

    # And a private file that should be ignored
    ignored_file = tmp_path / "_hidden.py"
    ignored_file.write_text(plugin_code, encoding="utf-8")

    discoverer = DirectoryPluginDiscoverer(tmp_path)
    results = discoverer.discover()

    assert len(results) == 1
    assert results[0].name == "DynamicPlugin"
    assert issubclass(results[0].plugin_cls, Plugin)

def test_directory_discoverer_empty_directory(tmp_path) -> None:
    """Empty directory should return an empty list of discovered plugins."""
    discoverer = DirectoryPluginDiscoverer(tmp_path)
    assert discoverer.discover() == []

def test_directory_discoverer_nonexistent_directory(tmp_path) -> None:
    """Nonexistent directory must raise PluginDiscoveryError."""
    fake_path = tmp_path / "does_not_exist"
    discoverer = DirectoryPluginDiscoverer(fake_path)

    with pytest.raises(PluginDiscoveryError, match="Directory not found"):
        discoverer.discover()
