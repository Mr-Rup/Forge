# 📋 Registry & Plugin Discovery

> **"Discovery finds what exists. The Registry remembers what is known. Neither cares how the plugins internally operate."**

This document covers Forge's **Plugin Registry** (`forge.core.registry`) and **Plugin Discovery** (`forge.core.discovery`).

---

## 📋 Phase 3: The Plugin Registry

The [PluginRegistry](../src/forge/core/registry.py) provides centralized bookkeeping of known plugins.

### Single Responsibility
The registry answers:
* *"Which plugins are currently registered?"*
* *"Is plugin 'csv' present?"*
* *"Give me the instance of plugin 'sql'."*

It does **not** know how plugins execute, how they load, or what features they provide.

```python
from forge.core.registry import PluginRegistry
from forge.plugins.hello import HelloPlugin

registry = PluginRegistry()
plugin = HelloPlugin()

# Registration & membership
registry.register(plugin)
assert "hello" in registry
assert registry.has("hello")

# Safe retrieval
p = registry.get("hello")

# Listing & iteration
names = registry.list_names()  # ['hello']
all_plugins = registry.list_all()
```

### Safety & Custom Exceptions
* **Duplicate Prevention**: Registering two plugins with the same `metadata.name` raises [PluginAlreadyRegisteredError](../src/forge/exceptions/plugin.py).
* **Missing Plugin Lookup**: Querying or unregistering a non-existent plugin raises [PluginNotFoundError](../src/forge/exceptions/plugin.py).

---

## 🔎 Phase 4: Plugin Discovery

Before a plugin can be registered or loaded, Forge must answer: **"Where are the candidate plugins?"**

### Separation of Concerns: Discovery vs. Loading
A common anti-pattern in plugin frameworks is merging discovery and loading into one giant function that imports, validates, constructs, and executes files all at once.

In Forge:
```mermaid
flowchart LR
    Discovery["Discovery<br/>What exists?"] --> Loading["Loading<br/>How do I instantiate it?"] --> Lifecycle["Lifecycle<br/>What state is it in?"]
```
Discovery inspects files and modules to identify plugin classes, producing lightweight **[DiscoveredPlugin](../src/forge/core/discovery.py)** descriptors **without instantiating them**.

```python
@dataclass(frozen=True)
class DiscoveredPlugin:
    name: str                  # Candidate class name
    plugin_cls: type[Plugin]   # The uninstantiated class reference
    source: str                # File path or module name
```

### Discovery Strategies

#### 1. `ModulePluginDiscoverer`
Scans an existing Python module or package (and its submodules):
```python
from forge.core.discovery import ModulePluginDiscoverer

discoverer = ModulePluginDiscoverer("forge.plugins")
candidates = discoverer.discover()
# Returns: [DiscoveredPlugin(name='HelloPlugin', plugin_cls=HelloPlugin, source='forge.plugins.hello')]
```

#### 2. `DirectoryPluginDiscoverer`
Scans any filesystem directory for `.py` files using dynamic module specs (`importlib.util`):
```python
from forge.core.discovery import DirectoryPluginDiscoverer

discoverer = DirectoryPluginDiscoverer("./custom_plugins")
candidates = discoverer.discover()
```

### Robust Candidate Filtering
The discoverers automatically filter out:
* 🚫 Abstract classes (`inspect.isabstract`)
* 🚫 The base `Plugin` class itself
* 🚫 Standard non-plugin classes, helper functions, and constants
* 🚫 Private files and modules (e.g. `__init__.py`, `_internal.py`)

If an invalid directory or unimportable module is passed, [PluginDiscoveryError](../src/forge/exceptions/plugin.py) is raised.

---

## 🔗 Next Chapter
Now that plugins can be discovered as lightweight candidate descriptors, how do we safely instantiate them and isolate crashes?

👉 Continue to **[Dynamic Loading Guide](./dynamic_loading.md)**.
