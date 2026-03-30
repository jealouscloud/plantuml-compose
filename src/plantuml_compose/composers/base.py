"""Base classes for the declarative composition API.

Provides EntityRef (returned by namespace factories) and BaseComposer
(the diagram object with d.add(), d.connect(), etc.).
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..primitives.common import (
    ColorLike,
    Footer,
    Header,
    Legend,
    Scale,
    sanitize_ref,
)


class EntityRef:
    """Reference to a composed entity with child access.

    Returned by namespace factories. Supports attribute access for
    children by sanitized name and bracket access for raw names.

    Example:
        wazuh = el.package("Wazuh",
            el.component("Agents / syscheckd", ref="agents"),
        )
        wazuh.agents          # child access by ref
        wazuh["Agents / syscheckd"]  # child access by raw name
    """

    __slots__ = ("_name", "_ref", "_data", "_children", "_children_by_name")

    def __init__(
        self,
        name: str,
        *,
        ref: str | None = None,
        data: dict[str, Any] | None = None,
        children: tuple[EntityRef, ...] = (),
    ) -> None:
        self._name = name
        self._ref = ref if ref else sanitize_ref(name)
        self._data = data or {}
        self._children: dict[str, EntityRef] = {}
        self._children_by_name: dict[str, EntityRef] = {}
        for child in children:
            self._children[child._ref] = child
            self._children_by_name[child._name] = child

    def __getattr__(self, name: str) -> EntityRef:
        # Only intercept attribute access for children, not internals
        if name.startswith("_"):
            raise AttributeError(name)
        children = object.__getattribute__(self, "_children")
        if name in children:
            return children[name]
        raise AttributeError(
            f"Entity {self._name!r} has no child with ref {name!r}. "
            f"Available: {list(children.keys())}"
        )

    def __getitem__(self, key: str) -> EntityRef:
        if key in self._children_by_name:
            return self._children_by_name[key]
        # Also try by ref
        if key in self._children:
            return self._children[key]
        raise KeyError(
            f"Entity {self._name!r} has no child {key!r}. "
            f"Available: {list(self._children_by_name.keys())}"
        )

    def __repr__(self) -> str:
        return f"<EntityRef {self._name!r} ref={self._ref!r}>"

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other


class BaseComposer:
    """Base class for diagram composers.

    Provides d.add(), d.connect(), d.note(), d.separator() and
    the build/render pattern. Common diagram metadata (title, mainframe,
    caption, header, footer, legend, scale) is stored here and passed
    through to primitives by each subclass's build().
    """

    def __init__(
        self,
        *,
        title: str | None = None,
        mainframe: str | None = None,
        caption: str | None = None,
        header: str | Header | None = None,
        footer: str | Footer | None = None,
        legend: str | Legend | None = None,
        scale: float | Scale | None = None,
    ) -> None:
        self._title = title
        self._mainframe = mainframe
        self._caption = caption
        self._header = header
        self._footer = footer
        self._legend = legend
        self._scale = scale
        self._elements: list[Any] = []
        self._connections: list[Any] = []
        self._notes: list[Any] = []

    def add(self, *items: Any) -> Any:
        """Register entities into the diagram.

        Returns what it receives — single item returns the item,
        multiple returns a tuple.
        """
        self._elements.extend(items)
        if len(items) == 1:
            return items[0]
        return items

    def connect(self, *connections: Any) -> None:
        """Register connections/relationships.

        Accepts variadic args or a single list.
        """
        for c in connections:
            if isinstance(c, list):
                self._connections.extend(c)
            else:
                self._connections.append(c)

    def note(
        self,
        content: str,
        *,
        target: EntityRef | str | None = None,
        position: str = "right",
        color: ColorLike | None = None,
    ) -> None:
        """Attach a note to the diagram or a target entity."""
        self._notes.append({
            "content": content,
            "target": target,
            "position": position,
            "color": color,
        })

    def separator(self, text: str = "") -> None:
        """Add a separator (diagram configuration, not an entity)."""
        self._elements.append(("__separator__", text))

    @abstractmethod
    def build(self) -> Any:
        """Build the frozen primitive diagram."""
        ...

    def render(self) -> str:
        """Build and render to PlantUML text."""
        from ..renderers import render as render_fn
        return render_fn(self.build())
