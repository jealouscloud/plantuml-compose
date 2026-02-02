"""SVG validation utilities for PlantUML output."""

import base64
import re


def check_svg_for_subdiagram_errors(svg_content: str) -> str | None:
    """
    Check SVG content for errors in embedded subdiagrams.

    Subdiagram errors are rendered inside base64-encoded images within the SVG.
    This function decodes those images and checks for error text.

    Args:
        svg_content: The SVG file content.

    Returns:
        Error message if found, None if no errors.
    """
    error_patterns = [
        "Syntax Error",
        "syntax error",
        "Error in diagram",
        "Diagram description contains errors",
    ]

    # Check main SVG text
    for pattern in error_patterns:
        if pattern in svg_content:
            return f"Error in SVG: '{pattern}'"

    # Check base64-encoded embedded images (subdiagrams)
    b64_pattern = r'(?:xlink:href|href)="data:image/[^;]+;base64,([^"]+)"'
    for match in re.finditer(b64_pattern, svg_content):
        b64_data = match.group(1)
        try:
            decoded = base64.b64decode(b64_data).decode("utf-8", errors="replace")
            for pattern in error_patterns:
                if pattern in decoded:
                    return f"Error in subdiagram: '{pattern}'"
        except Exception:
            try:
                decoded_bytes = base64.b64decode(b64_data)
                decoded_str = decoded_bytes.decode("latin-1", errors="replace")
                for pattern in error_patterns:
                    if pattern in decoded_str:
                        return f"Error in subdiagram: '{pattern}'"
            except Exception:
                pass

    return None
