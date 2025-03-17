"""
Formatting utilities for displaying systemd unit information.
"""

import os
from typing import List

from .manager import UnitStatus


class ConsoleFormatter:
    """Formatter for console output."""

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    @staticmethod
    def supports_color() -> bool:
        """Check if terminal supports colors."""
        # Check if NO_COLOR is set (see https://no-color.org/)
        if os.environ.get("NO_COLOR") is not None:
            return False

        # Check if output is a terminal
        return os.isatty(1)

    @staticmethod
    def color_text(text: str, color: str) -> str:
        """
        Color text if terminal supports colors.

        Args:
            text: Text to color
            color: Color name from COLORS dict

        Returns:
            Colored string if supported, original string otherwise
        """
        if not ConsoleFormatter.supports_color():
            return text

        color_code = ConsoleFormatter.COLORS.get(color, "")
        reset = ConsoleFormatter.COLORS["reset"]
        return f"{color_code}{text}{reset}"

    @staticmethod
    def format_unit_list(units: List[UnitStatus], show_header: bool = True) -> str:
        """
        Format a list of units for display.

        Args:
            units: List of UnitStatus objects
            show_header: Whether to show the header

        Returns:
            Formatted string for display
        """
        if not units:
            return "No units found."

        # Determine column widths
        name_width = max(max(len(unit.name) for unit in units), 20)
        load_width = max(max(len(unit.load_state) for unit in units), 10)
        active_width = max(max(len(unit.active_state) for unit in units), 10)
        sub_width = max(max(len(unit.sub_state) for unit in units), 10)

        # Build the result
        result = []

        # Add header
        if show_header:
            header = (
                f"{ConsoleFormatter.color_text('UNIT', 'bold'):{name_width}} "
                f"{ConsoleFormatter.color_text('LOAD', 'bold'):{load_width}} "
                f"{ConsoleFormatter.color_text('ACTIVE', 'bold'):{active_width}} "
                f"{ConsoleFormatter.color_text('SUB', 'bold'):{sub_width}} "
                f"{ConsoleFormatter.color_text('ENABLED', 'bold'):10} "
                f"{ConsoleFormatter.color_text('DESCRIPTION', 'bold')}"
            )
            result.append(header)
            result.append("-" * (name_width + load_width + active_width + sub_width + 50))

        # Add units
        for unit in units:
            # Color based on state
            name_color = "white"
            if unit.active_state == "active":
                name_color = "green"
            elif unit.active_state == "failed":
                name_color = "red"
            elif unit.active_state == "inactive":
                name_color = "yellow"

            # Color for enabled state
            enabled_text = "yes" if unit.enabled else "no"
            enabled_color = "green" if unit.enabled else "yellow"

            line = (
                f"{ConsoleFormatter.color_text(unit.name, name_color):{name_width}} "
                f"{unit.load_state:{load_width}} "
                f"{unit.active_state:{active_width}} "
                f"{unit.sub_state:{sub_width}} "
                f"{ConsoleFormatter.color_text(enabled_text, enabled_color):10} "
                f"{unit.description}"
            )
            result.append(line)

        return "\n".join(result)

    @staticmethod
    def format_unit_status(unit: UnitStatus) -> str:
        """
        Format detailed status of a unit.

        Args:
            unit: UnitStatus object

        Returns:
            Formatted string for display
        """
        if not unit:
            return "Unit not found."

        # Color based on state
        name_color = "white"
        if unit.active_state == "active":
            name_color = "green"
        elif unit.active_state == "failed":
            name_color = "red"
        elif unit.active_state == "inactive":
            name_color = "yellow"

        # Color for enabled state
        enabled_text = "enabled" if unit.enabled else "disabled"
        enabled_color = "green" if unit.enabled else "yellow"

        lines = [
            f"{ConsoleFormatter.color_text('●', name_color)} {ConsoleFormatter.color_text(unit.name, 'bold')} - {unit.description}",
            "",
            f"     Loaded: {unit.load_state}",
            f"     Active: {unit.active_state} ({unit.sub_state})",
            f"     Status: {ConsoleFormatter.color_text(enabled_text, enabled_color)}",
        ]

        return "\n".join(lines)