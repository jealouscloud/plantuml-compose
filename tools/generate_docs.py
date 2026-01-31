"""Generate documentation markdown with embedded PlantUML output.

This script reads markdown files from examples/base/, finds Python code blocks
that generate PlantUML diagrams, executes them, and inserts the resulting
PlantUML code in ```plantuml blocks immediately after the Python code.

The generated files are written to examples/.

Usage:
    uv run python tools/generate_docs.py

Code Block Format:
    In your base markdown, write Python code that prints PlantUML output:

    ```python
    from plantuml_compose import state_diagram

    with state_diagram(title="Example") as d:
        d.state("A")

    print(d.render())
    ```

    The script will execute this and insert:

    ```plantuml
    @startuml
    title Example
    state "A" as A
    @enduml
    ```

    directly after the Python block.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path


@dataclass
class DiagramInfo:
    """Information about a diagram extracted from markdown."""

    filename: str
    code: str
    output: str
    start_pos: int
    end_pos: int


def batch_verify_plantuml(diagrams: list[DiagramInfo]) -> dict[int, str]:
    """
    Verify multiple PlantUML diagrams in a single plantuml invocation.

    Args:
        diagrams: List of DiagramInfo objects to verify.

    Returns:
        Dict mapping diagram index to error message (only for failed diagrams).
    """
    if not diagrams:
        return {}

    if not shutil.which("plantuml"):
        # PlantUML not installed, skip verification
        return {}

    errors: dict[int, str] = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Write all diagrams to temp files
        for i, diagram in enumerate(diagrams):
            puml_file = tmp_path / f"diagram_{i:04d}.puml"
            puml_file.write_text(diagram.output)

        # Run plantuml once on the entire directory
        try:
            result = subprocess.run(
                ["plantuml", "-checkonly", str(tmp_path / "*.puml")],
                capture_output=True,
                text=True,
                timeout=60,
                shell=False,
            )

            # If there are errors, we need to identify which files failed
            # PlantUML returns non-zero and prints error info to stderr
            if result.returncode != 0:
                # Re-check each file individually to identify failures
                # This is still faster than checking each one separately from the start
                # because most diagrams will pass
                for i, diagram in enumerate(diagrams):
                    puml_file = tmp_path / f"diagram_{i:04d}.puml"
                    check_result = subprocess.run(
                        ["plantuml", "-checkonly", str(puml_file)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if check_result.returncode != 0:
                        errors[i] = (
                            check_result.stderr.strip() or "Unknown PlantUML error"
                        )

        except subprocess.TimeoutExpired:
            # On timeout, mark all as potentially failed
            for i in range(len(diagrams)):
                errors[i] = "PlantUML verification timed out"
        except Exception as e:
            for i in range(len(diagrams)):
                errors[i] = f"PlantUML verification failed: {e}"

    return errors


def encode_plantuml(text: str) -> str:
    """Encode PlantUML text for URL embedding."""
    # 1. UTF-8 encode
    data = text.encode("utf-8")

    # 2. Deflate compress (raw, no header)
    compressed = zlib.compress(data, 9)[2:-4]  # strip zlib header/checksum

    # 3. PlantUML's custom base64 encoding
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    result = []

    for i in range(0, len(compressed), 3):
        chunk = compressed[i : i + 3]
        b1 = chunk[0]
        b2 = chunk[1] if len(chunk) > 1 else 0
        b3 = chunk[2] if len(chunk) > 2 else 0

        result.append(alphabet[b1 >> 2])
        result.append(alphabet[((b1 & 0x3) << 4) | (b2 >> 4)])
        result.append(alphabet[((b2 & 0xF) << 2) | (b3 >> 6)])
        result.append(alphabet[b3 & 0x3F])

    return "".join(result)


def extract_python_blocks(content: str) -> list[tuple[int, int, str]]:
    """
    Extract Python code blocks from markdown content.

    Returns:
        List of (start_pos, end_pos, code) tuples for each ```python block.
    """
    pattern = r"```python\n(.*?)```"
    blocks = []
    for match in re.finditer(pattern, content, re.DOTALL):
        blocks.append((match.start(), match.end(), match.group(1)))
    return blocks


def execute_python_code(code: str) -> str | None:
    """
    Execute Python code and capture stdout.

    This uses Python's exec() to run code examples from documentation.
    The code is trusted documentation examples, not user input.

    Returns:
        Captured stdout, or None if execution fails or produces no output.
    """
    # Redirect stdout
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()

    try:
        # Execute in a fresh namespace with plantuml_compose available
        exec_globals: dict = {}
        # Using exec() here is intentional - we're running trusted Python
        # code examples from our own documentation to capture their output.
        # This is NOT shell execution - it's Python code execution.
        exec(code, exec_globals)  # noqa: S102
        output = captured.getvalue()
        return output.strip() if output.strip() else None
    except Exception as e:
        print(f"Error executing code: {e}", file=sys.stderr)
        print(f"Code:\n{code}", file=sys.stderr)
        return None
    finally:
        sys.stdout = old_stdout


def collect_diagrams(
    md_files: list[Path],
) -> tuple[dict[str, str], list[DiagramInfo]]:
    """
    Execute all Python blocks and collect diagram outputs.

    Returns:
        Tuple of (file_contents dict, list of DiagramInfo).
    """
    file_contents: dict[str, str] = {}
    all_diagrams: list[DiagramInfo] = []

    for md_file in md_files:
        content = md_file.read_text()
        file_contents[md_file.name] = content

        blocks = extract_python_blocks(content)
        for start, end, code in blocks:
            output = execute_python_code(code)
            if output:
                all_diagrams.append(
                    DiagramInfo(
                        filename=md_file.name,
                        code=code,
                        output=output,
                        start_pos=start,
                        end_pos=end,
                    )
                )

    return file_contents, all_diagrams


def generate_markdown_with_diagrams(
    file_contents: dict[str, str],
    diagrams: list[DiagramInfo],
    errors: dict[int, str],
) -> tuple[dict[str, str], list[str]]:
    """
    Generate final markdown content with embedded diagram URLs.

    Returns:
        Tuple of (processed file contents dict, list of error messages).
    """
    error_messages: list[str] = []

    # Group diagrams by file
    diagrams_by_file: dict[str, list[tuple[int, DiagramInfo]]] = {}
    for i, diagram in enumerate(diagrams):
        if diagram.filename not in diagrams_by_file:
            diagrams_by_file[diagram.filename] = []
        diagrams_by_file[diagram.filename].append((i, diagram))

    # Process each file
    processed_contents: dict[str, str] = {}

    for filename, content in file_contents.items():
        if filename not in diagrams_by_file:
            processed_contents[filename] = content
            continue

        # Process diagrams in reverse order to maintain position accuracy
        file_diagrams = sorted(
            diagrams_by_file[filename], key=lambda x: x[1].end_pos, reverse=True
        )

        for global_idx, diagram in file_diagrams:
            # Check for errors
            if global_idx in errors:
                code_lines = diagram.code.strip().split("\n")
                context = "\n".join(code_lines[:3])
                error_messages.append(
                    f"{filename}: PlantUML error:\n"
                    f"  Code: {context[:80]}...\n"
                    f"  Output: {diagram.output[:150]}...\n"
                    f"  Error: {errors[global_idx]}"
                )

            # Insert diagram URL
            encoded = encode_plantuml(diagram.output)
            url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
            plantuml_block = f"\n![Diagram]({url})\n\n"
            content = content[: diagram.end_pos] + plantuml_block + content[diagram.end_pos :]

        processed_contents[filename] = content

    return processed_contents, error_messages


def generate_docs(
    base_dir: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[list[Path], list[str]]:
    """
    Generate documentation from base markdown files.

    Args:
        base_dir: Source directory with base markdown files.
                  Defaults to examples/base/
        output_dir: Destination directory for generated files.
                    Defaults to examples/

    Returns:
        Tuple of (list of generated file paths, list of errors).
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent / "examples" / "base"
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "examples"

    base_dir = Path(base_dir)
    output_dir = Path(output_dir)

    if not base_dir.exists():
        print(f"Base directory does not exist: {base_dir}")
        return [], []

    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect all markdown files
    md_files = sorted(base_dir.glob("*.md"))
    if not md_files:
        print("No markdown files found in examples/base/")
        return [], []

    print(f"Processing {len(md_files)} markdown files...")

    # Phase 1: Execute all Python code and collect diagrams
    file_contents, diagrams = collect_diagrams(md_files)
    print(f"Found {len(diagrams)} diagrams to verify...")

    # Phase 2: Batch verify all diagrams (single plantuml invocation)
    errors = batch_verify_plantuml(diagrams)
    if errors:
        print(f"Found {len(errors)} diagram error(s)")

    # Phase 3: Generate final markdown
    processed_contents, error_messages = generate_markdown_with_diagrams(
        file_contents, diagrams, errors
    )

    # Write output files
    generated = []
    for filename, content in processed_contents.items():
        output_file = output_dir / filename
        output_file.write_text(content)
        generated.append(output_file)
        print(f"Generated: {output_file}")

    return generated, error_messages


if __name__ == "__main__":
    paths, errors = generate_docs()

    if errors:
        print(f"\n{len(errors)} PlantUML syntax error(s) detected:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if paths:
        print(f"\nGenerated {len(paths)} documentation files.")
    else:
        print("No markdown files found in examples/base/")
