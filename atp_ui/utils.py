from typing import Any, Dict, List, Optional, Union

# --- Utility Functions and Base Structure ---

def component_definition(
    category: str,
    component_type: str,
    props: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Standard structure for component definitions sent to the frontend.
    The frontend layer (React/Vue/etc.) maps 'component_type' to a specific
    visual component and applies the 'props'.
    """
    return {
        "category": category,
        "component_type": component_type,
        "props": props
    }