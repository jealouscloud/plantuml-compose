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