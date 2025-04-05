"""
Core functionality for interacting with systemd user units.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Union

from .utils import run_command, check_unit_exists


@dataclass
class UnitStatus:
    """Dataclass to represent the status of a systemd unit."""
    name: str
    load_state: str
    active_state: str
    sub_state: str
    description: str
    enabled: bool


class SystemdUnitManager:
    """Manager class for systemd user units."""

    @staticmethod
    def list_units(unit_type: Optional[str] = None) -> List[UnitStatus]:
        """
        List all user units or units of a specific type.

        Args:
            unit_type: Optional filter for unit type (service, timer, etc.)

        Returns:
            List of UnitStatus objects.
        """
        cmd = ["systemctl", "--user", "list-units", "--all"]
        if unit_type:
            cmd.append(f"*.{unit_type}")

        return_code, stdout, _ = run_command(cmd)
        if return_code != 0:
            return []

        units = []
        # Skip header and footer lines
        lines = stdout.strip().split("\n")

        # Find the data lines
        data_start = None
        data_end = None
        for i, line in enumerate(lines):
            if data_start is None and "UNIT" in line and "LOAD" in line and "ACTIVE" in line:
                data_start = i + 1
            if data_start is not None and data_end is None and not line.strip():
                data_end = i
                break

        if data_start is None or data_end is None:
            return []

        # Process data lines
        for line in lines[data_start:data_end]:
            if not line.strip():
                continue

            parts = line.split(maxsplit=4)
            if len(parts) < 5:
                continue

            name, load, active, sub, description = parts
            enabled = SystemdUnitManager.is_enabled(name)

            units.append(UnitStatus(
                name=name,
                load_state=load,
                active_state=active,
                sub_state=sub,
                description=description,
                enabled=enabled
            ))

        return units

    @staticmethod
    def get_unit_status(unit_name: str) -> Optional[UnitStatus]:
        """
        Get detailed status of a specific unit.

        Args:
            unit_name: Name of the unit

        Returns:
            UnitStatus object or None if unit doesn't exist
        """
        if not check_unit_exists(unit_name):
            return None

        # Get basic status
        cmd = ["systemctl", "--user", "show",
               "--property=LoadState,ActiveState,SubState,Description", unit_name]
        return_code, stdout, _ = run_command(cmd)
        if return_code != 0:
            return None

        properties = {}
        for line in stdout.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                properties[key] = value

        enabled = SystemdUnitManager.is_enabled(unit_name)

        return UnitStatus(
            name=unit_name,
            load_state=properties.get("LoadState", "unknown"),
            active_state=properties.get("ActiveState", "unknown"),
            sub_state=properties.get("SubState", "unknown"),
            description=properties.get("Description", ""),
            enabled=enabled
        )

    @staticmethod
    def start_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Start a systemd user unit.

        Args:
            unit_name: Name of the unit to start

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "start", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Started {unit_name} successfully"
        else:
            return False, f"Failed to start {unit_name}: {stderr}"

    @staticmethod
    def stop_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Stop a systemd user unit.

        Args:
            unit_name: Name of the unit to stop

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "stop", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Stopped {unit_name} successfully"
        else:
            return False, f"Failed to stop {unit_name}: {stderr}"

    @staticmethod
    def restart_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Restart a systemd user unit.

        Args:
            unit_name: Name of the unit to restart

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "restart", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Restarted {unit_name} successfully"
        else:
            return False, f"Failed to restart {unit_name}: {stderr}"

    @staticmethod
    def enable_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Enable a systemd user unit.

        Args:
            unit_name: Name of the unit to enable

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "enable", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Enabled {unit_name} successfully"
        else:
            return False, f"Failed to enable {unit_name}: {stderr}"

    @staticmethod
    def disable_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Disable a systemd user unit.

        Args:
            unit_name: Name of the unit to disable

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "disable", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Disabled {unit_name} successfully"
        else:
            return False, f"Failed to disable {unit_name}: {stderr}"

    @staticmethod
    def is_enabled(unit_name: str) -> bool:
        """
        Check if a unit is enabled.

        Args:
            unit_name: Name of the unit

        Returns:
            True if enabled, False otherwise
        """
        cmd = ["systemctl", "--user", "is-enabled", unit_name]
        return_code, stdout, _ = run_command(cmd)

        return return_code == 0 and stdout.strip() == "enabled"

    @staticmethod
    def mask_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Mask a systemd user unit to prevent it from being started.

        Args:
            unit_name: Name of the unit to mask

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "mask", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Masked {unit_name} successfully"
        else:
            return False, f"Failed to mask {unit_name}: {stderr}"

    @staticmethod
    def unmask_unit(unit_name: str) -> Tuple[bool, str]:
        """
        Unmask a systemd user unit to allow it to be started.

        Args:
            unit_name: Name of the unit to unmask

        Returns:
            Tuple of (success, message)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["systemctl", "--user", "unmask", unit_name]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, f"Unmasked {unit_name} successfully"
        else:
            return False, f"Failed to unmask {unit_name}: {stderr}"

    @staticmethod
    def get_journal_logs(unit_name: str, lines: int = 50) -> Tuple[bool, str]:
        """
        Get journal logs for a unit.

        Args:
            unit_name: Name of the unit
            lines: Number of log lines to retrieve

        Returns:
            Tuple of (success, logs)
        """
        if not check_unit_exists(unit_name):
            return False, f"Unit {unit_name} does not exist"

        cmd = ["journalctl", "--user", "-u", unit_name, "-n", str(lines)]
        return_code, stdout, stderr = run_command(cmd)

        if return_code == 0:
            return True, stdout
        else:
            return False, f"Failed to retrieve logs for {unit_name}: {stderr}"
