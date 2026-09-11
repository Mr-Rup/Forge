"""Plugin validation engine for verifying plugin metadata and contract compliance."""

from dataclasses import dataclass, field
import re
from typing import List

from forge.contracts.plugin import Plugin, PluginMetadata
from forge.exceptions.plugin import PluginValidationError

# Identifier pattern: alphanumeric, dashes, and underscores
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Semantic version pattern: e.g., 1.0, 1.0.0, 1.0.0-beta
VERSION_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9_.]+)?$")

@dataclass
class ValidationResult:
    """Holds outcome and error messages from a validation check."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)

class PluginValidator:
    """Validates that a plugin satisfies metadata and contract requirements."""

    def validate_metadata(self, metadata: PluginMetadata) -> List[str]:
        """Validate metadata fields and return any error messages."""
        errors: List[str] = []

        if not metadata.name or not metadata.name.strip():
            errors.append("Plugin name cannot be empty.")
        elif not NAME_PATTERN.match(metadata.name):
            errors.append(
                f"Invalid plugin name '{metadata.name}'. Name must be alphanumeric with '-' or '_'."
            )

        if not metadata.version or not metadata.version.strip():
            errors.append("Plugin version cannot be empty.")
        elif not VERSION_PATTERN.match(metadata.version):
            errors.append(
                f"Invalid plugin version '{metadata.version}'. Expected format like '1.0.0'."
            )

        if not metadata.description or not metadata.description.strip():
            errors.append("Plugin description cannot be empty.")

        if not metadata.author or not metadata.author.strip():
            errors.append("Plugin author cannot be empty.")

        return errors

    def validate_contract(self, plugin: Plugin) -> List[str]:
        """Validate that the plugin implements required contract methods."""
        errors: List[str] = []

        if not isinstance(plugin, Plugin):
            errors.append(
                f"Object '{type(plugin).__name__}' is not an instance of Plugin."
            )
            return errors

        for method_name in ("initialize", "execute", "shutdown"):
            method = getattr(plugin, method_name, None)
            if method is None or not callable(method):
                errors.append(
                    f"Plugin is missing required callable method '{method_name}'."
                )

        return errors

    def check(self, plugin: Plugin) -> ValidationResult:
        """Run validation checks and return a ValidationResult."""
        errors: List[str] = []

        if not hasattr(plugin, "metadata") or not isinstance(
            plugin.metadata, PluginMetadata
        ):
            errors.append("Plugin is missing a valid PluginMetadata instance.")
        else:
            errors.extend(self.validate_metadata(plugin.metadata))

        errors.extend(self.validate_contract(plugin))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate(self, plugin: Plugin) -> None:
        """Validate plugin and raise PluginValidationError if any check fails."""
        result = self.check(plugin)
        if not result.is_valid:
            error_details = "; ".join(result.errors)
            raise PluginValidationError(
                f"Plugin validation failed: {error_details}",
                errors=result.errors,
            )
