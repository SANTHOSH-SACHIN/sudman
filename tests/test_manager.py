"""
Tests for the SystemdUnitManager class.
"""

import unittest
from unittest.mock import patch

from sudman.manager import SystemdUnitManager, UnitStatus


class TestSystemdUnitManager(unittest.TestCase):
    """Test cases for SystemdUnitManager."""

    @patch('sudman.manager.run_command')
    @patch('sudman.manager.check_unit_exists')
    def test_list_units(self, mock_check_unit_exists, mock_run_command):
        """Test listing units."""
        # Mock the command output
        mock_run_command.return_value = (0, """
UNIT                                  LOAD   ACTIVE SUB     DESCRIPTION
foo.service                           loaded active running Foo Service
bar.service                           loaded active running Bar Service
baz.timer                             loaded active waiting Baz Timer

3 loaded units listed.
        """, "")

        # Mock the is_enabled method
        with patch.object(SystemdUnitManager, 'is_enabled',
                          side_effect=[True, False, True]):
            units = SystemdUnitManager.list_units()

        # Assertions
        self.assertEqual(len(units), 3)
        self.assertEqual(units[0].name, "foo.service")
        self.assertEqual(units[0].load_state, "loaded")
        self.assertEqual(units[0].active_state, "active")
        self.assertEqual(units[0].sub_state, "running")
        self.assertEqual(units[0].description, "Foo Service")
        self.assertTrue(units[0].enabled)

        self.assertEqual(units[1].name, "bar.service")
        self.assertFalse(units[1].enabled)

        self.assertEqual(units[2].name, "baz.timer")
        self.assertTrue(units[2].enabled)

    @patch('sudman.manager.run_command')
    @patch('sudman.manager.check_unit_exists')
    def test_get_unit_status(self, mock_check_unit_exists, mock_run_command):
        """Test getting unit status."""
        # Mock the unit exists check
        mock_check_unit_exists.return_value = True

        # Mock the command output
        mock_run_command.return_value = (0, """
LoadState=loaded
ActiveState=active
SubState=running
Description=Foo Service
        """, "")

        # Mock the is_enabled method
        with patch.object(SystemdUnitManager, 'is_enabled', return_value=True):
            unit = SystemdUnitManager.get_unit_status("foo.service")

        # Assertions
        self.assertEqual(unit.name, "foo.service")
        self.assertEqual(unit.load_state, "loaded")
        self.assertEqual(unit.active_state, "active")
        self.assertEqual(unit.sub_state, "running")
        self.assertEqual(unit.description, "Foo Service")
        self.assertTrue(unit.enabled)

    @patch('sudman.manager.run_command')
    @patch('sudman.manager.check_unit_exists')
    def test_start_unit(self, mock_check_unit_exists, mock_run_command):
        """Test starting a unit."""
        # Mock the unit exists check
        mock_check_unit_exists.return_value = True

        # Mock the command output
        mock_run_command.return_value = (0, "", "")

        # Call the method
        success, message = SystemdUnitManager.start_unit("foo.service")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Started foo.service successfully")
        mock_run_command.assert_called_once_with(
            ["systemctl", "--user", "start", "foo.service"]
        )

    @patch('sudman.manager.run_command')
    @patch('sudman.manager.check_unit_exists')
    def test_stop_unit(self, mock_check_unit_exists, mock_run_command):
        """Test stopping a unit."""
        # Mock the unit exists check
        mock_check_unit_exists.return_value = True

        # Mock the command output
        mock_run_command.return_value = (0, "", "")

        # Call the method
        success, message = SystemdUnitManager.stop_unit("foo.service")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Stopped foo.service successfully")
        mock_run_command.assert_called_once_with(
            ["systemctl", "--user", "stop", "foo.service"]
        )

    @patch('sudman.manager.run_command')
    @patch('sudman.manager.check_unit_exists')
    def test_enable_unit(self, mock_check_unit_exists, mock_run_command):
        """Test enabling a unit."""
        # Mock the unit exists check
        mock_check_unit_exists.return_value = True

        # Mock the command output
        mock_run_command.return_value = (0, "", "")

        # Call the method
        success, message = SystemdUnitManager.enable_unit("foo.service")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Enabled foo.service successfully")
        mock_run_command.assert_called_once_with(
            ["systemctl", "--user", "enable", "foo.service"]
        )

    @patch('sudman.manager.run_command')
    def test_is_enabled(self, mock_run_command):
        """Test checking if a unit is enabled."""
        # Mock the command output for enabled unit
        mock_run_command.return_value = (0, "enabled\n", "")

        # Call the method
        enabled = SystemdUnitManager.is_enabled("foo.service")

        # Assertions
        self.assertTrue(enabled)
        mock_run_command.assert_called_once_with(
            ["systemctl", "--user", "is-enabled", "foo.service"]
        )

        # Mock the command output for disabled unit
        mock_run_command.reset_mock()
        mock_run_command.return_value = (1, "disabled\n", "")

        # Call the method
        enabled = SystemdUnitManager.is_enabled("bar.service")

        # Assertions
        self.assertFalse(enabled)