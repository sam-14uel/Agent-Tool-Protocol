import json
from typing import Any, Dict, List, Optional, Union

from.utils import component_definition

# --- 1. Layout Classes ---

class Layout:
    """
    Defines foundational elements for structure and responsiveness.
    """
    CATEGORY = "Layout"

    @staticmethod
    def Breakpoints(extra_breakpoints: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Defines the core responsive screen sizes for media queries."""
        defaults = {
            "xs": "0px",
            "sm": "576px",
            "md": "768px",
            "lg": "992px",
            "xl": "1200px",
            "xxl": "1400px"
        }
        if extra_breakpoints:
            defaults.update(extra_breakpoints)
        return component_definition(Layout.CATEGORY, "Breakpoints", {"definitions": defaults})

    @staticmethod
    def Container(fluid: bool = False, max_width: Optional[str] = None) -> Dict[str, Any]:
        """A responsive fixed-width or fluid container for page content."""
        return component_definition(Layout.CATEGORY, "Container", {
            "fluid": fluid,
            "maxWidth": max_width,
            "description": "Wraps content with responsive padding and centering."
        })

    @staticmethod
    def Grid(columns: int = 12, direction: str = 'row') -> Dict[str, Any]:
        """Defines the base grid system properties."""
        return component_definition(Layout.CATEGORY, "Grid", {
            "columns": columns,
            "direction": direction,
            "behavior": "flexbox"
        })

    @staticmethod
    def Column(size: Union[int, str], breakpoint: str = 'default', content: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """A single column within a grid row, defining its span across breakpoints."""
        return component_definition(Layout.CATEGORY, "Column", {
            "size": size,
            "breakpoint": breakpoint,
            "content": content if content is not None else [],
        })

    @staticmethod
    def Gutters(spacing_unit: str = 'rem', spacing_map: Dict[str, float] = None) -> Dict[str, Any]:
        """Configuration for spacing utilities between grid elements (gutters)."""
        if spacing_map is None:
            spacing_map = {"0": 0, "1": 0.25, "2": 0.5, "3": 1, "4": 1.5, "5": 3}
        return component_definition(Layout.CATEGORY, "Gutters", {
            "unit": spacing_unit,
            "map": spacing_map
        })

    @staticmethod
    def ZIndex(layers: Dict[str, int]) -> Dict[str, Any]:
        """Configuration for the Z-index layering utility for overlays and modals."""
        return component_definition(Layout.CATEGORY, "Z-index", {
            "layers": layers
        })

    @staticmethod
    def CSSGrid(template_columns: str = 'repeat(12, 1fr)', template_rows: str = 'auto') -> Dict[str, Any]:
        """Alternative configuration for pure CSS Grid layout."""
        return component_definition(Layout.CATEGORY, "CSS Grid", {
            "template_columns": template_columns,
            "template_rows": template_rows,
            "description": "Explicit CSS Grid layout properties."
        })