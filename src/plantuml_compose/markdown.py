"""Markdown processing for PlantUML diagram generation.

Finds Python code blocks that import plantuml_compose, executes them,
and inserts rendered diagram server URLs into the markdown.

Idempotent — re-running replaces existing diagram URLs rather than
duplicating them.
"""

from __future__ import annotations

import re
import sys
from io import StringIO
from typing import NamedTuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .renderers.common import DEFAULT_PLANTUML_SERVER, render_url

# Matches a "plantuml unit": an optional <details> wrapper around a
# python code block, followed by an optional ![Diagram](...) line.
_UNIT_RE = re.compile(
    r"(?P<details_open><details>\s*\n\s*<summary>[^<]*</summary>\s*\n\s*)?"
    r"```python\n(?P<code>.*?)```"
    r"(?P<details_close>\s*\n\s*</details>)?"
    r"(?P<diagram>\s*\n\s*!\[Diagram\]\([^\)]+\))?",
    re.DOTALL,
)


_PLANTUML_IMPORT_RE = re.compile(
    r"(?:^|\s)import\s+plantuml_compose|(?:^|\s)from\s+plantuml_compose"
)


def _has_plantuml_import(code: str) -> bool:
    """Check if a code block imports plantuml_compose."""
    return _PLANTUML_IMPORT_RE.search(code) is not None


def _execute_code(code: str) -> str | None:
    """Execute Python code and capture stdout.

    Returns:
        Captured stdout stripped, or None on failure / no output.
    """
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    try:
        # Executes trusted documentation code blocks that import plantuml_compose.
        # This is the core mechanism: code blocks print PlantUML text to stdout.
        exec(code, {})  # noqa: S102
        output = captured.getvalue()
        return output.strip() if output.strip() else None
    except Exception as e:
        print(f"Error executing code block: {e}", file=sys.stderr)
        return None
    finally:
        sys.stdout = old_stdout


class ValidationError(NamedTuple):
    diagram_index: int
    url: str
    error: str
    line: str | None


def validate_urls(urls: list[str], timeout: int = 10) -> list[ValidationError]:
    """Validate diagram URLs against the PlantUML server via HEAD requests.

    Checks the x-plantuml-diagram-error response header which the server
    sets on syntax errors.

    Args:
        urls: List of PlantUML server URLs to validate
        timeout: Request timeout in seconds

    Returns:
        List of ValidationErrors for diagrams that failed
    """
    errors: list[ValidationError] = []
    for i, url in enumerate(urls, start=1):
        try:
            req = Request(
                url,
                method="HEAD",
                headers={"User-Agent": "puml-md/1.0"},
            )
            with urlopen(req, timeout=timeout) as resp:
                diag_error = resp.headers.get("x-plantuml-diagram-error")
                if diag_error:
                    errors.append(ValidationError(
                        diagram_index=i,
                        url=url,
                        error=diag_error,
                        line=resp.headers.get("x-plantuml-diagram-error-line"),
                    ))
        except HTTPError as e:
            # 400 responses still carry plantuml diagnostic headers
            diag_error = e.headers.get("x-plantuml-diagram-error")
            if diag_error:
                errors.append(ValidationError(
                    diagram_index=i, url=url, error=diag_error,
                    line=e.headers.get("x-plantuml-diagram-error-line"),
                ))
            else:
                errors.append(ValidationError(
                    diagram_index=i, url=url, error=f"HTTP {e.code}", line=None,
                ))
        except (URLError, OSError) as e:
            errors.append(ValidationError(
                diagram_index=i, url=url, error=str(e), line=None,
            ))
    return errors


def process_markdown(
    content: str,
    *,
    details: bool = False,
    server: str = DEFAULT_PLANTUML_SERVER,
    format: str = "svg",
) -> tuple[str, list[str]]:
    """Process markdown, executing Python blocks and inserting diagram URLs.

    Finds ```python code blocks that import plantuml_compose, executes
    them, and inserts/replaces ![Diagram](...) image links with rendered
    PlantUML server URLs.

    Args:
        content: Markdown text to process
        details: Wrap code blocks in <details><summary>Code</summary>
        server: PlantUML server base URL
        format: Output format for diagram URLs (svg, png, etc.)

    Returns:
        Tuple of (processed markdown, list of generated URLs)
    """
    generated_urls: list[str] = []

    def _replacer(match: re.Match) -> str:
        code = match.group("code")
        if not _has_plantuml_import(code):
            return match.group(0)

        output = _execute_code(code)
        if output is None:
            return match.group(0)

        url = render_url(output, server=server, format=format)
        generated_urls.append(url)
        code_block = f"```python\n{code}```"
        already_wrapped = match.group("details_open") is not None

        if already_wrapped or details:
            return (
                f"<details>\n<summary>Code</summary>\n\n"
                f"{code_block}\n\n"
                f"</details>\n\n"
                f"![Diagram]({url})"
            )
        return f"{code_block}\n\n![Diagram]({url})"

    result = _UNIT_RE.sub(_replacer, content)
    return result, generated_urls
