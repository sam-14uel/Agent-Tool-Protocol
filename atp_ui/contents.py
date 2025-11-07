import json
from typing import Any, Dict, List, Optional, Union

# --- Utility Functions and Base Structure ---

from.utils import component_definition


# --- 2. Content Classes ---

class Content:
    """
    Defines styles for basic HTML content elements.
    """
    CATEGORY = "Content"

    @staticmethod
    def Reboot() -> Dict[str, Any]:
        """Configuration for CSS resets/normalizes and base styling."""
        return component_definition(Content.CATEGORY, "Reboot", {
            "normalize_css": True,
            "box_sizing": "border-box",
            "font_family": "system-ui"
        })

    @staticmethod
    def Typography(tag: str = 'p', style: str = 'body', text: str = 'Default text content') -> Dict[str, Any]:
        """Styles and defines text elements (headings, paragraphs, links)."""
        return component_definition(Content.CATEGORY, "Typography", {
            "tag": tag, # e.g., 'h1', 'p', 'a'
            "style": style, # e.g., 'h1', 'lead', 'muted'
            "text": text
        })

    @staticmethod
    def Images(src: str, alt: str = '', responsive: bool = True, rounded: bool = False) -> Dict[str, Any]:
        """Defines image elements and their display properties."""
        return component_definition(Content.CATEGORY, "Images", {
            "src": src,
            "alt": alt,
            "responsive": responsive,
            "rounded": rounded
        })

    @staticmethod
    def Tables(data: List[List[Any]], striped: bool = False, hover: bool = True) -> Dict[str, Any]:
        """Configuration for structured tabular data."""
        return component_definition(Content.CATEGORY, "Tables", {
            "data_rows": len(data),
            "striped": striped,
            "hover": hover,
            "data_preview_schema": data[0] if data else [] # Show schema of the first row
        })

    @staticmethod
    def Figures(img_src: str, caption: str) -> Dict[str, Any]:
        """Defines a component for displaying an image with an associated caption."""
        return component_definition(Content.CATEGORY, "Figures", {
            "image_src": img_src,
            "caption": caption
        })