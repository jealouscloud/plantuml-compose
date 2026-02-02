"""Base classes and mixins for diagram builders."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..primitives import EmbeddedDiagram


class EmbeddableDiagramMixin:
    """Mixin that provides embed() functionality for diagram builders.

    This mixin provides the ability to embed a diagram inside another diagram's
    notes, messages, or legends using PlantUML's {{ }} sub-diagram syntax.

    Builders should inherit from this mixin and implement:
        - build(): Return the diagram primitive
        - render(): Return the PlantUML text

    For specialized diagram types (Gantt, MindMap, WBS, JSON, YAML) that need
    to keep their @start.../@end... markers, set _keep_diagram_markers = True.

    Example:
        class MyDiagramBuilder(EmbeddableDiagramMixin):
            def build(self) -> MyDiagram:
                ...

            def render(self) -> str:
                ...

        # For specialized diagrams that keep markers:
        class GanttDiagramBuilder(EmbeddableDiagramMixin):
            _keep_diagram_markers = True
            ...
    """

    # Set to True for specialized diagrams that need their markers preserved
    # (Gantt, MindMap, WBS, JSON, YAML)
    _keep_diagram_markers: bool = False

    @abstractmethod
    def build(self) -> Any:
        """Build and return the diagram primitive."""
        ...

    @abstractmethod
    def render(self) -> str:
        """Build and render the diagram to PlantUML text."""
        ...

    def embed(self, *, transparent: bool = True) -> EmbeddedDiagram:
        """Return this diagram as an embeddable sub-diagram.

        Use in notes, messages, or legends of other diagrams.

        Args:
            transparent: If True, applies transparent background styling.

        Returns:
            EmbeddedDiagram that can be used in note content, messages, etc.

        Example:
            # Build a component diagram to embed
            with component_diagram() as arch:
                api = arch.component("API")
                db = arch.component("DB")
                arch.link(api, db)

            # Embed it in a sequence diagram note
            with sequence_diagram() as d:
                alice = d.participant("Alice")
                d.note(arch.embed(), position="right", of=alice)
        """
        return EmbeddedDiagram(
            content=self._render_inner(),
            transparent=transparent,
        )

    def _render_inner(self) -> str:
        """Render diagram content for embedding.

        For standard diagrams: strips @startuml/@enduml wrapper.
        For specialized diagrams (Gantt, MindMap, etc.): keeps markers
        because PlantUML needs them to identify the diagram type.

        Returns:
            PlantUML content suitable for embedding in {{ }} blocks.
        """
        full = self.render()

        if self._keep_diagram_markers:
            # Specialized diagrams need their markers preserved
            return full

        # Standard diagrams: strip the @startuml/@enduml wrapper
        lines = full.split("\n")
        inner_lines = [
            line for line in lines
            if not line.strip().startswith("@startuml")
            and not line.strip().startswith("@enduml")
        ]
        return "\n".join(inner_lines)
