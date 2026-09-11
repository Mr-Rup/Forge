"""Unit tests for plugin validation and error hierarchy."""

import pytest

from forge.contracts.plugin import Plugin, PluginMetadata
from forge.core.loader import PluginLoader
from forge.core.validator import PluginValidator, ValidationResult
from forge.exceptions.base import ForgeError
from forge.exceptions.configuration import ConfigurationError
from forge.exceptions.plugin import PluginValidationError
from forge.plugins.hello import HelloPlugin

class ValidCustomPlugin(Plugin):
    """Auxiliary valid plugin."""

    def __init__(self, name: str = "valid-plugin", version: str = "1.0.0") -> None:
        super().__init__(
            PluginMetadata(
                name=name,
                version=version,
                description="Valid description.",
                author="Author",
            )
        )

    def initialize(self) -> None:
        pass

    def execute(self) -> str:
        return "done"

    def shutdown(self) -> None:
        pass

def test_valid_plugin_passes_validation() -> None:
    """Verify standard valid plugins pass validation checks."""
    validator = PluginValidator()
    plugin = HelloPlugin()

    result = validator.check(plugin)
    assert result.is_valid
    assert len(result.errors) == 0

    # validate() should not raise
    validator.validate(plugin)

def test_invalid_name_raises_error() -> None:
    """Names with spaces, empty strings, or symbols must fail validation."""
    validator = PluginValidator()

    # Name with spaces and special symbol
    bad_plugin = ValidCustomPlugin(name="bad name!")
    result = validator.check(bad_plugin)
    assert not result.is_valid
    assert any("Invalid plugin name" in err for err in result.errors)

    with pytest.raises(PluginValidationError, match="Invalid plugin name"):
        validator.validate(bad_plugin)

    # Empty name
    empty_name_plugin = ValidCustomPlugin(name="")
    result_empty = validator.check(empty_name_plugin)
    assert not result_empty.is_valid
    assert any("Plugin name cannot be empty" in err for err in result_empty.errors)

def test_invalid_version_raises_error() -> None:
    """Non-semver strings must fail validation."""
    validator = PluginValidator()

    bad_ver_plugin = ValidCustomPlugin(version="latest-version")
    result = validator.check(bad_ver_plugin)

    assert not result.is_valid
    assert any("Invalid plugin version" in err for err in result.errors)

    with pytest.raises(PluginValidationError, match="Invalid plugin version"):
        validator.validate(bad_ver_plugin)

def test_semver_formats_accepted() -> None:
    """Standard semantic version formats should be accepted."""
    validator = PluginValidator()

    for valid_ver in ("1.0", "1.0.0", "2.1.3-beta", "0.0.1-rc.1"):
        plugin = ValidCustomPlugin(version=valid_ver)
        result = validator.check(plugin)
        assert result.is_valid, f"Version '{valid_ver}' should be valid"

def test_multiple_errors_aggregated() -> None:
    """ValidationResult should collect all detected issues."""
    class MessyPlugin(Plugin):
        def __init__(self) -> None:
            super().__init__(
                PluginMetadata(
                    name="invalid name!",
                    version="not_semver",
                    description="",
                    author="",
                )
            )

        def initialize(self) -> None:
            pass

        def execute(self) -> None:
            pass

        def shutdown(self) -> None:
            pass

    validator = PluginValidator()
    result = validator.check(MessyPlugin())

    assert not result.is_valid
    assert len(result.errors) >= 4
    # All 4 metadata fields have errors
    assert any("name" in e.lower() for e in result.errors)
    assert any("version" in e.lower() for e in result.errors)
    assert any("description" in e.lower() for e in result.errors)
    assert any("author" in e.lower() for e in result.errors)

def test_loader_rejects_invalid_plugin() -> None:
    """PluginLoader must reject invalid plugins before transition to LOADED."""
    class InvalidMetadataPlugin(Plugin):
        def __init__(self) -> None:
            super().__init__(
                PluginMetadata(
                    name="invalid name!",
                    version="1.0.0",
                    description="Desc",
                    author="Author",
                )
            )

        def initialize(self) -> None:
            pass

        def execute(self) -> None:
            pass

        def shutdown(self) -> None:
            pass

    loader = PluginLoader()
    with pytest.raises(PluginValidationError):
        loader.load(InvalidMetadataPlugin)

def test_configuration_error_hierarchy() -> None:
    """ConfigurationError must inherit from ForgeError."""
    assert issubclass(ConfigurationError, ForgeError)
