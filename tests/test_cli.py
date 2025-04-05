"""
Tests for the command-line interface.
"""

import unittest
from unittest.mock import patch, MagicMock

from sudman.cli import main, create_parser
from sudman.manager import UnitStatus


class TestCLI(unittest.TestCase):
    """Test cases for the CLI."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        self.assertEqual(parser.prog, "sudman")

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    def test_main_no_args(self, mock_is_user_session_active, mock_is_systemd_available):
        """Test main function with no arguments."""
        mock_is_systemd_available.return_value = True
        mock_is_user_session_active.return_value = True

        with patch('sys.stdout') as mock_stdout:
            exit_code = main([])

        self.assertEqual(exit_code, 0)

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    def test_systemd_not_available(self, mock_is_user_session_active, mock_is_systemd_available):
        """Test behavior when systemd is not available."""
        mock_is_systemd_available.return_value = False
        mock_is_user_session_active.return_value = True

        with patch('builtins.print') as mock_print:
            exit_code = main(["unit", "list"])

        self.assertEqual(exit_code, 1)
        mock_print.assert_called_once_with("Error: systemd is not available on this system.")

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    def test_user_session_not_active(self, mock_is_user_session_active, mock_is_systemd_available):
        """Test behavior when user session is not active."""
        mock_is_systemd_available.return_value = True
        mock_is_user_session_active.return_value = False

        with patch('builtins.print') as mock_print:
            exit_code = main(["unit", "list"])

        self.assertEqual(exit_code, 1)
        mock_print.assert_called_once_with("Error: systemd user session is not active.")

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    @patch('sudman.cli.SystemdUnitManager.list_units')
    @patch('sudman.cli.ConsoleFormatter.format_unit_list')
    def test_list_command(self, mock_format, mock_list_units,
                          mock_is_user_session_active, mock_is_systemd_available):
        """Test the list command."""
        mock_is_systemd_available.return_value = True
        mock_is_user_session_active.return_value = True

        # Mock the list_units method
        units = [
            UnitStatus(
                name="foo.service",
                load_state="loaded",
                active_state="active",
                sub_state="running",
                description="Foo Service",
                enabled=True
            )
        ]
        mock_list_units.return_value = units

        # Mock the format_unit_list method
        mock_format.return_value = "Formatted output"

        with patch('builtins.print') as mock_print:
            exit_code = main(["unit", "list"])

        self.assertEqual(exit_code, 0)
        mock_list_units.assert_called_once_with(None)
        mock_format.assert_called_once_with(units)
        mock_print.assert_called_once_with("Formatted output")

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    @patch('sudman.cli.SystemdUnitManager.get_unit_status')
    @patch('sudman.cli.ConsoleFormatter.format_unit_status')
    def test_status_command(self, mock_format, mock_get_status,
                            mock_is_user_session_active, mock_is_systemd_available):
        """Test the status command."""
        mock_is_systemd_available.return_value = True
        mock_is_user_session_active.return_value = True

        # Mock the get_unit_status method
        unit = UnitStatus(
            name="foo.service",
            load_state="loaded",
            active_state="active",
            sub_state="running",
            description="Foo Service",
            enabled=True
        )
        mock_get_status.return_value = unit

        # Mock the format_unit_status method
        mock_format.return_value = "Formatted status"

        with patch('builtins.print') as mock_print:
            exit_code = main(["unit", "status", "foo.service"])

        self.assertEqual(exit_code, 0)
        mock_get_status.assert_called_once_with("foo.service")
        mock_format.assert_called_once_with(unit)
        mock_print.assert_called_once_with("Formatted status")

    @patch('sudman.cli.is_systemd_available')
    @patch('sudman.cli.is_user_session_active')
    @patch('sudman.cli.SystemdUnitManager.start_unit')
    def test_start_command(self, mock_start_unit,
                           mock_is_user_session_active, mock_is_systemd_available):
        """Test the start command."""
        mock_is_systemd_available.return_value = True
        mock_is_user_session_active.return_value = True

        # Mock the start_unit method
        mock_start_unit.return_value = (True, "Started foo.service successfully")

        with patch('builtins.print') as mock_print:
            exit_code = main(["unit", "start", "foo.service"])

        self.assertEqual(exit_code, 0)
        mock_start_unit.assert_called_once_with("foo.service")
        mock_print.assert_called_once_with("Started foo.service successfully")
