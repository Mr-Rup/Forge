"""Demonstration HelloPlugin implementation."""

from forge.contracts.plugin import Plugin, PluginMetadata


class HelloPlugin(Plugin):
    """Simple demonstration plugin returning greetings."""

    def __init__(self) -> None:
        metadata = PluginMetadata(
            name="hello",
            version="1.0.0",
            description="A simple demonstration plugin.",
            author="Rup",
        )
        super().__init__(metadata)

    def initialize(self) -> None:
        """Initialize resources for HelloPlugin."""
        pass

    def execute(self) -> str:
        """Execute greeting logic."""
        return "Hello from Forge!"

    def shutdown(self) -> None:
        """Clean up resources on shutdown."""
        pass
