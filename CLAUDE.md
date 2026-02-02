# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

plantuml-compose is a Python library that wraps PlantUML syntax generation in type-safe Python. The library must:

- Organize diagram types with specific supported syntax for each
- Be capable of outputting all potential diagrams expressible in PlantUML text syntax
- Use `PLANTUML_SYNTAX_REFERENCE.md` as the authoritative syntax reference

## Development Commands

```bash
# Install dependencies
uv sync

# Run the CLI
uv run plantuml-compose

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_name -v

# Test PlantUML output
plantuml <filename>              # Generate diagram
plantuml --check-syntax <filename>  # Validate syntax only
```

## Project Structure

- `src/plantuml_compose/` - Main package source code
- `examples/` - Example PlantUML diagram files
- `PLANTUML_SYNTAX_REFERENCE.md` - Authoritative PlantUML syntax reference (v1.2025.0)

## Technical Details

- Python 3.13+ required
- Uses `uv` for dependency management and building
- Entry point: `plantuml-compose` CLI command (defined in pyproject.toml)

## Architecture

Three-layer architecture:
```
Layer 3: Builders (state_diagram, etc.) - User-facing API with context managers
Layer 2: Renderers (render) - Pure functions transforming primitives to PlantUML text
Layer 1: Primitives (frozen dataclasses) - Immutable domain model
```

## Design Principles

### Only Expose What PlantUML Actually Renders

PlantUML accepts syntax that it silently ignores. Our builder API must only expose parameters that have visible effect. This prevents user frustration from setting options that do nothing.

**Process for new features:**
1. Test the raw PlantUML syntax to confirm it renders visually
2. Generate SVG output and verify the styling appears
3. Only then expose the parameter in the builder API

**Example:** Fork/join bars accept `#color` syntax but always render gray. We removed the `style` parameter from `fork()` and `join()` builder methods, though the underlying `PseudoState` primitive retains the field for future compatibility.

**Canary tests:** `tests/test_plantuml_limitations.py` contains tests that verify PlantUML limitations still exist. If PlantUML adds support for a feature, these tests will fail, signaling we can expose the parameter.

### Primitives vs Builders

- **Primitives** (Layer 1): Complete data model, may include fields PlantUML ignores
- **Builders** (Layer 3): Honest API, only exposes what works
- **Renderers** (Layer 2): Render all primitive fields, even if PlantUML ignores them

This separation allows advanced users to construct primitives directly while protecting typical users from non-functional options.