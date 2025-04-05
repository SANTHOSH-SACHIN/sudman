"""
Command-line interface for sudman.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .manager import SystemdUnitManager
from .formatters import ConsoleFormatter
from .utils import is_systemd_available, is_user_session_active


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="sudman",
        description="Systemd User Daemon Manager - A user-friendly interface for systemd user units",
    )

    parser.add_argument(
        "--version", action="version", version=f"sudman v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Interactive command
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Start interactive TUI mode"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List systemd user units")
    list_parser.add_argument(
        "--type", help="Filter by unit type (service, timer, etc.)"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show status of a unit")
    status_parser.add_argument("unit", help="Unit name")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a unit")
    start_parser.add_argument("unit", help="Unit name")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a unit")
    stop_parser.add_argument("unit", help="Unit name")

    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart a unit")
    restart_parser.add_argument("unit", help="Unit name")

    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a unit")
    enable_parser.add_argument("unit", help="Unit name")

    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a unit")
    disable_parser.add_argument("unit", help="Unit name")

    # Mask command
    mask_parser = subparsers.add_parser("mask", help="Mask a unit to prevent it from being started")
    mask_parser.add_argument("unit", help="Unit name")

    # Unmask command
    unmask_parser = subparsers.add_parser("unmask", help="Unmask a unit to allow it to be started")
    unmask_parser.add_argument("unit", help="Unit name")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show logs for a unit")
    logs_parser.add_argument("unit", help="Unit name")
    logs_parser.add_argument(
        "-n", "--lines", type=int, default=50, help="Number of log lines to show"
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.command is None:
        parser.print_help()
        return 0

    # Check if systemd is available
    if not is_systemd_available():
        print("Error: systemd is not available on this system.")
        return 1

    # Check if user session is active
    if not is_user_session_active():
        print("Error: systemd user session is not active.")
        return 1

    # Execute the requested command
    if parsed_args.command == "list":
        units = SystemdUnitManager.list_units(parsed_args.type)
        print(ConsoleFormatter.format_unit_list(units))

    elif parsed_args.command == "status":
        unit = SystemdUnitManager.get_unit_status(parsed_args.unit)
        if unit:
            print(ConsoleFormatter.format_unit_status(unit))
        else:
            print(f"Unit {parsed_args.unit} not found.")
            return 1

    elif parsed_args.command == "start":
        success, message = SystemdUnitManager.start_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "stop":
        success, message = SystemdUnitManager.stop_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "restart":
        success, message = SystemdUnitManager.restart_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "enable":
        success, message = SystemdUnitManager.enable_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "disable":
        success, message = SystemdUnitManager.disable_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "mask":
        success, message = SystemdUnitManager.mask_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "unmask":
        success, message = SystemdUnitManager.unmask_unit(parsed_args.unit)
        print(message)
        return 0 if success else 1

    elif parsed_args.command == "logs":
        success, logs = SystemdUnitManager.get_journal_logs(
            parsed_args.unit, parsed_args.lines
        )
        if success:
            print(logs)
        else:
            print(logs)  # logs contains error message
            return 1

    elif parsed_args.command == "interactive":
        from .interactive import run_interactive
        run_interactive()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
