"""Generate markdown gallery of test output PNGs per module."""

import ast
import re
from pathlib import Path
from collections import defaultdict


def extract_test_source(test_file: Path, class_name: str, test_name: str) -> str | None:
    """
    Extract the source code of a test method from a test file.

    Uses ast to find line numbers, then extracts the raw source.
    """
    if not test_file.exists():
        return None

    # Handle parametrized tests (e.g., test_name__0 -> test_name)
    base_test_name = re.sub(r"__\d+$", "", test_name)

    source = test_file.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == base_test_name:
                    # Extract source lines
                    lines = source.splitlines()
                    start = item.lineno - 1
                    end = item.end_lineno
                    return "\n".join(lines[start:end])
    return None


def generate_module_gallery(module_dir: Path, tests_dir: Path) -> Path | None:
    """
    Generate a markdown file for a single test module's PNG outputs.

    Args:
        module_dir: Directory containing PNGs (e.g., tests/output/test_state/)
        tests_dir: Directory containing test files (e.g., tests/)

    Returns:
        Path to generated gallery.md, or None if no PNGs found.
    """
    pngs = sorted(module_dir.glob("*.png"))

    if not pngs:
        return None

    module_name = module_dir.name  # e.g., "test_state"
    test_file = tests_dir / f"{module_name}.py"
    output_file = module_dir / "gallery.md"

    # Group by test class (part before __)
    grouped: dict[str, list[Path]] = defaultdict(list)
    for png in pngs:
        parts = png.stem.split("__", 1)
        class_name = parts[0] if len(parts) > 1 else "Other"
        grouped[class_name].append(png)

    # Format module name for title (test_state -> State Diagram Tests)
    title_name = module_name.replace("test_", "").replace("_", " ").title()
    lines = [f"# {title_name} Tests\n"]

    for class_name in sorted(grouped.keys()):
        lines.append(f"## {class_name}\n")

        for png in grouped[class_name]:
            # Extract test name (part after __)
            parts = png.stem.split("__", 1)
            test_name = parts[1] if len(parts) > 1 else png.stem

            lines.append(f"### {test_name}\n")

            # Include test source code
            source = extract_test_source(test_file, class_name, test_name)
            if source:
                lines.append("```python")
                lines.append(source)
                lines.append("```\n")

            lines.append(f"![{test_name}]({png.name})\n")

    content = "\n".join(lines)
    output_file.write_text(content)
    return output_file


def generate_all_galleries(
    output_dir: Path = Path(__file__).parent.parent / "tests/output",
) -> list[Path]:
    """
    Generate markdown galleries for all test modules.

    Iterates over subdirectories in output_dir and generates a gallery.md
    for each module that has PNG files.

    Returns:
        List of paths to generated gallery files.
    """
    tests_dir = output_dir.parent
    generated = []

    for module_dir in sorted(output_dir.iterdir()):
        if module_dir.is_dir():
            result = generate_module_gallery(module_dir, tests_dir)
            if result:
                generated.append(result)

    return generated


if __name__ == "__main__":
    paths = generate_all_galleries()
    if paths:
        print(f"Generated {len(paths)} gallery files:")
        for p in paths:
            print(f"  {p}")
    else:
        print("No PNG files found in any module directory.")
