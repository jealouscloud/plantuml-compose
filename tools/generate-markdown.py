"""Generate markdown gallery of test output PNGs."""

import ast
import re
from pathlib import Path
from collections import defaultdict


def extract_test_source(tests_dir: Path, class_name: str, test_name: str) -> str | None:
    """
    Extract the source code of a test method from test files.

    Uses ast to find line numbers, then extracts the raw source.
    """
    # Handle parametrized tests (e.g., test_name__0 -> test_name)
    base_test_name = re.sub(r"__\d+$", "", test_name)

    for test_file in tests_dir.glob("test_*.py"):
        source = test_file.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

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


def generate_test_gallery(
    output_dir: Path = Path(__file__).parent.parent / "tests/output",
    output_file: Path | None = None,
) -> Path:
    """
    Generate a markdown file embedding all PNG test outputs.

    Groups images by test class and includes the test name and source code.
    """
    if output_file is None:
        output_file = output_dir / "gallery.md"

    tests_dir = output_dir.parent

    pngs = sorted(output_dir.glob("*.png"))

    if not pngs:
        raise FileNotFoundError(f"No PNG files found in {output_dir}")

    # Group by test class (part before __)
    grouped: dict[str, list[Path]] = defaultdict(list)
    for png in pngs:
        parts = png.stem.split("__", 1)
        class_name = parts[0] if len(parts) > 1 else "Other"
        grouped[class_name].append(png)

    lines = ["# Test Output Gallery\n"]

    for class_name in sorted(grouped.keys()):
        lines.append(f"## {class_name}\n")

        for png in grouped[class_name]:
            # Extract test name (part after __)
            parts = png.stem.split("__", 1)
            test_name = parts[1] if len(parts) > 1 else png.stem

            lines.append(f"### {test_name}\n")

            # Include test source code
            source = extract_test_source(tests_dir, class_name, test_name)
            if source:
                lines.append("```python")
                lines.append(source)
                lines.append("```\n")

            lines.append(f"![{test_name}]({png.name})\n")

    content = "\n".join(lines)
    output_file.write_text(content)
    return output_file


if __name__ == "__main__":
    path = generate_test_gallery()
    print(f"Generated: {path}")
