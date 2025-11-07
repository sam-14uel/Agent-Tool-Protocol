import json
from typing import Any, Dict, List, Optional, Union

# --- Utility Functions and Base Structure ---

from.utils import component_definition

# --- 3. Forms Classes ---

class Forms:
    """
    Defines classes for user input and form controls.
    """
    CATEGORY = "Forms"

    @staticmethod
    def FormControl(type: str = 'text', label: str = 'Input Field', placeholder: str = '') -> Dict[str, Any]:
        """Base configuration for a single text, email, password, etc., input control."""
        return component_definition(Forms.CATEGORY, "Form control", {
            "type": type,
            "label": label,
            "placeholder": placeholder,
            "required": False
        })

    @staticmethod
    def Select(label: str, options: List[str], multiple: bool = False) -> Dict[str, Any]:
        """Configuration for a dropdown select box."""
        return component_definition(Forms.CATEGORY, "Select", {
            "label": label,
            "options": options,
            "multiple": multiple
        })

    @staticmethod
    def ChecksRadios(type: str = 'checkbox', label: str = 'Option', checked: bool = False) -> Dict[str, Any]:
        """Configuration for checkboxes or radio buttons."""
        return component_definition(Forms.CATEGORY, "Checks & radios", {
            "input_type": type,
            "label": label,
            "checked": checked
        })

    @staticmethod
    def Range(label: str, min_val: int = 0, max_val: int = 100, step: int = 1) -> Dict[str, Any]:
        """Configuration for a range input slider."""
        return component_definition(Forms.CATEGORY, "Range", {
            "label": label,
            "min": min_val,
            "max": max_val,
            "step": step
        })

    @staticmethod
    def InputGroup(prepend_text: Optional[str] = None, append_text: Optional[str] = None, input_type: str = 'text') -> Dict[str, Any]:
        """Configuration for an input with prepended/appended text, icons, or buttons."""
        return component_definition(Forms.CATEGORY, "Input group", {
            "prepend": prepend_text,
            "append": append_text,
            "input_type": input_type
        })

    @staticmethod
    def FloatingLabels(label: str, input_type: str = 'text') -> Dict[str, Any]:
        """Configuration for an input field where the label floats above the input on focus."""
        return component_definition(Forms.CATEGORY, "Floating labels", {
            "label": label,
            "input_type": input_type
        })

    @staticmethod
    def Layout(direction: str = 'vertical', alignment: str = 'start') -> Dict[str, Any]:
        """Configuration for grouping and aligning form elements."""
        return component_definition(Forms.CATEGORY, "Layout", {
            "direction": direction, # 'vertical' or 'horizontal'
            "alignment": alignment # e.g., 'start', 'center'
        })

    @staticmethod
    def Validation(state: str = 'invalid', message: str = 'Field is required.') -> Dict[str, Any]:
        """Configuration for displaying form validation status and feedback messages."""
        return component_definition(Forms.CATEGORY, "Validation", {
            "state": state, # 'valid', 'invalid'
            "feedback_message": message
        })
