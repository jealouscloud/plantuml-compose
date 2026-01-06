"""Generate markdown gallery of test output PNGs."""

from pathlib import Path
from collections import defaultdict


def generate_test_gallery(
    output_dir: Path = Path(__file__).parent.parent / "tests/output",
    output_file: Path | None = None,
) -> Path:
    """
    Generate a markdown file embedding all PNG test outputs.

    Groups images by test class and includes the test name as caption.
    """
    if output_file is None:
        output_file = output_dir / "gallery.md"

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
            lines.append(f"![{test_name}]({png.name})\n")

    content = "\n".join(lines)
    output_file.write_text(content)
    return output_file


if __name__ == "__main__":
    path = generate_test_gallery()
    print(f"Generated: {path}")
