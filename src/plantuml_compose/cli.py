"""CLI for plantuml-compose."""

from __future__ import annotations

import argparse
import sys

from .markdown import process_markdown, validate_urls
from .renderers.common import DEFAULT_PLANTUML_SERVER


def _add_md_args(parser: argparse.ArgumentParser) -> None:
    """Add markdown processing arguments to a parser."""
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Input markdown file (default: stdin)",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Modify file in place",
    )
    parser.add_argument(
        "-d",
        "--details",
        action="store_true",
        help="Wrap code blocks in <details><summary>",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Check generated diagrams against the PlantUML server",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_PLANTUML_SERVER,
        help=f"PlantUML server URL (default: {DEFAULT_PLANTUML_SERVER})",
    )
    parser.add_argument(
        "--format",
        default="svg",
        help="Diagram output format: svg, png, txt, etc. (default: svg)",
    )


def _run_md(args: argparse.Namespace) -> None:
    """Run markdown processing with parsed args."""
    if args.in_place and args.file == "-":
        print("error: --in-place requires a file argument", file=sys.stderr)
        sys.exit(2)

    # Read input
    if args.file == "-":
        content = sys.stdin.read()
    else:
        with open(args.file) as f:
            content = f.read()

    # Process
    result, urls = process_markdown(
        content,
        details=args.details,
        server=args.server,
        format=args.format,
    )

    # Validate before writing
    if args.validate and urls:
        errors = validate_urls(urls)
        if errors:
            for err in errors:
                loc = f" (line {err.line})" if err.line else ""
                print(
                    f"diagram {err.diagram_index}{loc}: {err.error}",
                    file=sys.stderr,
                )
            sys.exit(1)

    # Write output
    if args.in_place:
        with open(args.file, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)


def markdown() -> None:
    """Entry point for puml-md standalone command."""
    parser = argparse.ArgumentParser(
        prog="puml-md",
        description="Process markdown with embedded PlantUML Python code blocks.",
    )
    _add_md_args(parser)
    args = parser.parse_args()
    _run_md(args)


def main() -> None:
    """Entry point for plantuml-compose with subcommands."""
    parser = argparse.ArgumentParser(
        prog="plantuml-compose",
        description="PlantUML Compose — type-safe PlantUML diagram generation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    md_parser = subparsers.add_parser(
        "md",
        help="Process markdown with embedded PlantUML Python code blocks",
    )
    _add_md_args(md_parser)

    args = parser.parse_args()

    if args.command == "md":
        _run_md(args)
    else:
        parser.print_help()
