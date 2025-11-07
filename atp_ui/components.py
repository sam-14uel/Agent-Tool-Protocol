import json
from typing import Any, Dict, List, Optional, Union

# --- Utility Functions and Base Structure ---

from.utils import component_definition

# --- 4. Components Classes ---

class Components:
    """
    Defines interactive, reusable UI components.
    """
    CATEGORY = "Components"

    @staticmethod
    def Accordion(items: List[Dict[str, str]], always_open: bool = False) -> Dict[str, Any]:
        """A collapsible content container."""
        return component_definition(Components.CATEGORY, "Accordion", {
            "items": items, # [{"header": "Item 1", "body": "Content 1"}]
            "always_open": always_open
        })

    @staticmethod
    def Alerts(message: str, type: str = 'info', dismissible: bool = False) -> Dict[str, Any]:
        """Provides contextual feedback messages to the user."""
        return component_definition(Components.CATEGORY, "Alerts", {
            "message": message,
            "type": type, # 'success', 'danger', 'warning', 'info'
            "dismissible": dismissible
        })

    @staticmethod
    def Badge(content: str, color: str = 'primary', pill: bool = False) -> Dict[str, Any]:
        """Small counting and labeling component."""
        return component_definition(Components.CATEGORY, "Badge", {
            "content": content,
            "color": color,
            "pill": pill
        })

    @staticmethod
    def Breadcrumb(links: List[Dict[str, str]]) -> Dict[str, Any]:
        """Indicates the current page's location within a navigational hierarchy."""
        return component_definition(Components.CATEGORY, "Breadcrumb", {
            "links": links # [{"label": "Home", "url": "/"}, ...]
        })

    @staticmethod
    def Buttons(label: str, variant: str = 'primary', size: str = 'medium', disabled: bool = False) -> Dict[str, Any]:
        """Custom button styles for user actions."""
        return component_definition(Components.CATEGORY, "Buttons", {
            "label": label,
            "variant": variant, # 'primary', 'secondary', 'success', 'danger'
            "size": size, # 'small', 'medium', 'large'
            "disabled": disabled
        })

    @staticmethod
    def ButtonGroup(buttons: List[Dict[str, Any]], vertical: bool = False) -> Dict[str, Any]:
        """Groups a series of buttons together on a single line."""
        return component_definition(Components.CATEGORY, "Button group", {
            "buttons": buttons, # List of Button definitions
            "vertical": vertical
        })

    @staticmethod
    def Card(header: Optional[str] = None, body: str = '', footer: Optional[str] = None) -> Dict[str, Any]:
        """A flexible and extensible content container."""
        return component_definition(Components.CATEGORY, "Card", {
            "header": header,
            "body": body,
            "footer": footer
        })

    @staticmethod
    def Carousel(items: List[Dict[str, str]], indicators: bool = True, controls: bool = True) -> Dict[str, Any]:
        """A slideshow component for cycling through images or elements."""
        return component_definition(Components.CATEGORY, "Carousel", {
            "items": items, # [{"src": "img1.jpg", "caption": "Slide 1"}]
            "indicators": indicators,
            "controls": controls
        })

    @staticmethod
    def CloseButton(label: str = 'Close') -> Dict[str, Any]:
        """A generic close icon for dismissing content like modals and alerts."""
        return component_definition(Components.CATEGORY, "Close button", {
            "aria_label": label
        })

    @staticmethod
    def Collapse(target_id: str, show: bool = False) -> Dict[str, Any]:
        """Toggles the visibility of content (hide/show) via JavaScript and CSS."""
        return component_definition(Components.CATEGORY, "Collapse", {
            "target_id": target_id,
            "show": show
        })

    @staticmethod
    def Dropdowns(label: str, items: List[Dict[str, str]]) -> Dict[str, Any]:
        """Toggleable, contextual overlay menus for actions."""
        return component_definition(Components.CATEGORY, "Dropdowns", {
            "label": label,
            "items": items # [{"label": "Action", "action_id": "a1"}]
        })

    @staticmethod
    def ListGroup(items: List[str], numbered: bool = False, flush: bool = False) -> Dict[str, Any]:
        """A flexible component for displaying a series of content in a list."""
        return component_definition(Components.CATEGORY, "List group", {
            "items": items,
            "numbered": numbered,
            "flush": flush
        })

    @staticmethod
    def Modal(title: str, body: str, size: str = 'medium', backdrop_static: bool = False) -> Dict[str, Any]:
        """A dialog prompt/box over the user's main content."""
        return component_definition(Components.CATEGORY, "Modal", {
            "title": title,
            "body": body,
            "size": size, # 'small', 'medium', 'large'
            "backdrop_static": backdrop_static
        })

    @staticmethod
    def Navbar(brand_name: str, links: List[Dict[str, str]], fixed: str = 'none') -> Dict[str, Any]:
        """A responsive navigation header."""
        return component_definition(Components.CATEGORY, "Navbar", {
            "brand": brand_name,
            "links": links, # [{"label": "Link", "url": "/link"}]
            "fixed": fixed # 'top', 'bottom', 'none'
        })

    @staticmethod
    def NavsTabs(items: List[str], type: str = 'nav') -> Dict[str, Any]:
        """Configuration for navigational components (simple nav links or tab controls)."""
        return component_definition(Components.CATEGORY, "Navs & tabs", {
            "items": items,
            "type": type # 'nav' or 'tabs'
        })

    @staticmethod
    def Offcanvas(title: str, body: str, placement: str = 'start') -> Dict[str, Any]:
        """A sidebar component that slides into the viewport."""
        return component_definition(Components.CATEGORY, "Offcanvas", {
            "title": title,
            "body": body,
            "placement": placement # 'start', 'end', 'top', 'bottom'
        })

    @staticmethod
    def Pagination(current_page: int, total_pages: int) -> Dict[str, Any]:
        """A set of linked buttons for navigation through paginated content."""
        return component_definition(Components.CATEGORY, "Pagination", {
            "current": current_page,
            "total": total_pages
        })

    @staticmethod
    def Placeholders(lines: int = 3, size: str = 'default') -> Dict[str, Any]:
        """Loading placeholders for content that is still fetching/rendering."""
        return component_definition(Components.CATEGORY, "Placeholders", {
            "lines": lines,
            "size": size # 'small', 'large'
        })

    @staticmethod
    def Popovers(trigger: str = 'hover', content: str = 'This is a popover message.') -> Dict[str, Any]:
        """Small overlay content containers for secondary information, visible on hover/click."""
        return component_definition(Components.CATEGORY, "Popovers", {
            "trigger": trigger,
            "content": content
        })

    @staticmethod
    def Progress(value: int, max_val: int = 100, label: Optional[str] = None) -> Dict[str, Any]:
        """Displays the progress of a task."""
        return component_definition(Components.CATEGORY, "Progress", {
            "value": value,
            "max": max_val,
            "label": label
        })

    @staticmethod
    def Scrollspy(target_id: str, nav_items: List[str]) -> Dict[str, Any]:
        """Automatically updates nav or list group components based on scroll position."""
        return component_definition(Components.CATEGORY, "Scrollspy", {
            "target_id": target_id,
            "nav_items": nav_items
        })

    @staticmethod
    def Spinners(style: str = 'border', color: str = 'primary', size: str = 'default') -> Dict[str, Any]:
        """Indicates a loading or processing state."""
        return component_definition(Components.CATEGORY, "Spinners", {
            "style": style, # 'border' or 'grow'
            "color": color,
            "size": size # 'small' or 'default'
        })

    @staticmethod
    def Toasts(title: str, message: str, delay_ms: int = 5000) -> Dict[str, Any]:
        """A lightweight, temporary notification component, appearing in a corner."""
        return component_definition(Components.CATEGORY, "Toasts", {
            "title": title,
            "message": message,
            "delay_ms": delay_ms
        })

    @staticmethod
    def Tooltips(placement: str = 'top', content: str = 'Hint message') -> Dict[str, Any]:
        """A small, contextual popup for help text, visible on hover/focus."""
        return component_definition(Components.CATEGORY, "Tooltips", {
            "placement": placement,
            "content": content
        })