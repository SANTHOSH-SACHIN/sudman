"""
Utility functions for the sudman package.
"""

import os
import subprocess
from typing import List, Tuple, Optional


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, and stderr.

    Args:
        cmd: The command to run as a list of strings.

    Returns:
        Tuple containing (return_code, stdout, stderr)
    """
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)


def is_systemd_available() -> bool:
    """Check if systemd is available on the system."""
    return_code, _, _ = run_command(["systemctl", "--version"])
    return return_code == 0


def is_user_session_active() -> bool:
    """Check if a systemd user session is active."""
    return_code, _, _ = run_command(["systemctl", "--user", "status"])
    return return_code != 1  # Return code 1 means systemd is not running


def get_unit_file_path(unit_name: str) -> Optional[str]:
    """
    Get the path to a user unit file.

    Args:
        unit_name: The name of the unit file.

    Returns:
        Path to the unit file or None if not found.
    """
    possible_paths = [
        os.path.expanduser(f"~/.config/systemd/user/{unit_name}"),
        f"/usr/lib/systemd/user/{unit_name}",
        f"/etc/systemd/user/{unit_name}"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def check_unit_exists(unit_name: str) -> bool:
    """
    Check if a unit exists.

    Args:
        unit_name: The name of the unit.

    Returns:
        True if the unit exists, False otherwise.
    """
    cmd = ["systemctl", "--user", "list-unit-files", unit_name]
    return_code, stdout, _ = run_command(cmd)

    if return_code != 0:
        return False

    # If no unit files match, systemctl will return 0 but with a specific output
    return "0 unit files listed." not in stdout