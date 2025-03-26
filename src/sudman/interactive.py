"""
Interactive TUI interface for sudman.
"""

import curses
from typing import List, Optional

from .manager import UnitStatus
from .formatters import ConsoleFormatter


class SudmanTUI:
    """Text-based user interface for sudman."""

    def __init__(self):
        self.screen = None
        self.units: List[UnitStatus] = []
        self.selected_idx = 0
        self.filter_type: Optional[str] = None
        self.offset = 0
        self.max_lines = 0

    def init_curses(self):
        """Initialize curses settings."""
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        curses.curs_set(0)  # Hide cursor

        # Enable colors if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_RED, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)
            curses.init_pair(4, curses.COLOR_WHITE, -1)
            curses.init_pair(5, curses.COLOR_CYAN, -1)

    def cleanup(self):
        """Clean up curses settings."""
        if self.screen:
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()

    def load_units(self):
        """Load units from systemd."""
        from .manager import SystemdUnitManager
        self.units = SystemdUnitManager.list_units(self.filter_type)

    def draw(self):
        """Draw the TUI interface."""
        if not self.screen:
            return

        self.screen.clear()
        height, width = self.screen.getmaxyx()

        # Calculate how many lines we can display
        self.max_lines = height - 4  # Leave space for header and footer

        # Draw header
        header = "Systemd User Units Manager (sudman)"
        if self.filter_type:
            header += f" - Filter: {self.filter_type}"
        self.screen.addstr(0, 0, header, curses.A_BOLD)
        self.screen.addstr(1, 0, "Use arrow keys to navigate, Enter to select, q to quit", curses.A_DIM)

        # Draw unit list
        visible_units = self.units[self.offset:self.offset + self.max_lines]
        for i, unit in enumerate(visible_units):
            line_num = i + 2
            if line_num >= height - 1:
                break  # Prevent writing past bottom of screen

            # Highlight selected unit
            attr = curses.A_REVERSE if (i + self.offset) == self.selected_idx else curses.A_NORMAL

            # Color based on state
            color_pair = 0
            if unit.active_state == "active":
                color_pair = 1
            elif unit.active_state == "failed":
                color_pair = 2
            elif unit.active_state == "inactive":
                color_pair = 3
            else:
                color_pair = 4

            # Format the line
            enabled_text = "✓" if unit.enabled else "✗"
            line = f"{unit.name[:width-10]:<{width-10}} {enabled_text:>3}"

            self.screen.addstr(line_num, 0, line, attr | curses.color_pair(color_pair))

        # Draw footer
        footer = f"Units: {len(self.units)} | Selected: {self.selected_idx + 1}/{len(self.units)}"
        if len(self.units) > self.max_lines:
            footer += f" | Showing {self.offset + 1}-{min(self.offset + self.max_lines, len(self.units))}"
        self.screen.addstr(height - 1, 0, footer, curses.A_DIM)

        self.screen.refresh()

    def show_unit_details(self, unit: UnitStatus):
        """Show detailed view for a unit."""
        if not self.screen:
            return

        height, width = self.screen.getmaxyx()
        self.screen.clear()

        # Show unit name and description
        self.screen.addstr(0, 0, f"Unit: {unit.name}", curses.A_BOLD)
        self.screen.addstr(1, 0, f"Description: {unit.description}")

        # Show status information
        self.screen.addstr(3, 0, "Status:")
        self.screen.addstr(4, 2, f"Loaded: {unit.load_state}")

        # Color active state
        color = curses.color_pair(1) if unit.active_state == "active" else \
                curses.color_pair(2) if unit.active_state == "failed" else \
                curses.color_pair(3) if unit.active_state == "inactive" else \
                curses.color_pair(4)
        self.screen.addstr(5, 2, f"Active: {unit.active_state} ({unit.sub_state})", color)

        # Color enabled state
        enabled_color = curses.color_pair(1) if unit.enabled else curses.color_pair(3)
        self.screen.addstr(6, 2, f"Enabled: {'yes' if unit.enabled else 'no'}", enabled_color)

        # Show actions
        self.screen.addstr(8, 0, "Actions:", curses.A_BOLD)
        self.screen.addstr(9, 2, "s - Start")
        self.screen.addstr(10, 2, "t - Stop")
        self.screen.addstr(11, 2, "r - Restart")
        self.screen.addstr(12, 2, "e - Enable")
        self.screen.addstr(13, 2, "d - Disable")
        self.screen.addstr(14, 2, "l - View logs")
        self.screen.addstr(15, 2, "b - Back to list")

        self.screen.refresh()

    def run(self):
        """Main TUI loop."""
        try:
            self.init_curses()
            self.load_units()

            while True:
                self.draw()
                key = self.screen.getch()

                if key == ord('q'):
                    break
                elif key == curses.KEY_UP and self.selected_idx > 0:
                    self.selected_idx -= 1
                    if self.selected_idx < self.offset:
                        self.offset = max(0, self.offset - 1)
                elif key == curses.KEY_DOWN and self.selected_idx < len(self.units) - 1:
                    self.selected_idx += 1
                    if self.selected_idx >= self.offset + self.max_lines:
                        self.offset += 1
                elif key == curses.KEY_ENTER or key == 10 or key == 13:
                    if self.units:
                        self.handle_unit_selection(self.units[self.selected_idx])
                elif key == ord('f'):
                    self.handle_filter_input()
                elif key == ord('r'):
                    self.load_units()  # Refresh list

        finally:
            self.cleanup()

    def handle_unit_selection(self, unit: UnitStatus):
        """Handle selection of a unit."""
        while True:
            self.show_unit_details(unit)
            key = self.screen.getch()

            if key == ord('b'):
                break
            elif key == ord('s'):
                from .manager import SystemdUnitManager
                success, message = SystemdUnitManager.start_unit(unit.name)
                self.show_message(message)
            elif key == ord('t'):
                from .manager import SystemdUnitManager
                success, message = SystemdUnitManager.stop_unit(unit.name)
                self.show_message(message)
            elif key == ord('r'):
                from .manager import SystemdUnitManager
                success, message = SystemdUnitManager.restart_unit(unit.name)
                self.show_message(message)
            elif key == ord('e'):
                from .manager import SystemdUnitManager
                success, message = SystemdUnitManager.enable_unit(unit.name)
                self.show_message(message)
            elif key == ord('d'):
                from .manager import SystemdUnitManager
                success, message = SystemdUnitManager.disable_unit(unit.name)
                self.show_message(message)
            elif key == ord('l'):
                from .manager import SystemdUnitManager
                success, logs = SystemdUnitManager.get_journal_logs(unit.name, 20)
                self.show_message(logs if success else f"Error: {logs}")

    def show_message(self, message: str):
        """Show a message to the user."""
        if not self.screen:
            return

        height, width = self.screen.getmaxyx()
        self.screen.clear()
        self.screen.addstr(0, 0, "Message:", curses.A_BOLD)

        # Split message into lines that fit the screen
        lines = []
        for line in message.split('\n'):
            while len(line) > width:
                lines.append(line[:width])
                line = line[width:]
            lines.append(line)

        # Display lines (with max height constraint)
        for i, line in enumerate(lines[:height-3]):
            self.screen.addstr(i+2, 0, line)

        self.screen.addstr(height-1, 0, "Press any key to continue...", curses.A_DIM)
        self.screen.refresh()
        self.screen.getch()

    def handle_filter_input(self):
        """Handle input for filtering units by type."""
        if not self.screen:
            return

        height, width = self.screen.getmaxyx()
        self.screen.clear()
        self.screen.addstr(0, 0, "Filter by unit type (e.g. service, timer):", curses.A_BOLD)
        self.screen.addstr(1, 0, "Leave empty to clear filter")

        # Enable echo for input
        curses.echo()
        curses.curs_set(1)
        self.screen.refresh()

        try:
            input_str = self.screen.getstr(2, 0, 20).decode('utf-8').strip()
            self.filter_type = input_str if input_str else None
            self.selected_idx = 0
            self.offset = 0
            self.load_units()
        finally:
            curses.noecho()
            curses.curs_set(0)


def run_interactive():
    """Run the interactive TUI."""
    tui = SudmanTUI()
    tui.run()
