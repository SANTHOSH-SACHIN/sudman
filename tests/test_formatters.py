"""
Tests for the formatters module.
"""

import unittest
from unittest.mock import patch

from sudman.formatters import ConsoleFormatter
from sudman.manager import UnitStatus


class TestConsoleFormatter(unittest.TestCase):
    """Test cases for ConsoleFormatter."""

    def test_supports_color(self):
        """Test color support detection."""
        # Mock os.environ.get to return None for NO_COLOR
        with patch('os.environ.get', return_value=None):
            # Mock os.isatty to return True
            with patch('os.isatty', return_value=True):
                self.assertTrue(ConsoleFormatter.supports_color())

            # Mock os.isatty to return False
            with patch('os.isatty', return_value=False):
                self.assertFalse(ConsoleFormatter.supports_color())

        # Mock os.environ.get to return a value for NO_COLOR
        with patch('os.environ.get', return_value="1"):
            # Mock os.isatty to return True (should still be False due to NO_COLOR)
            with patch('os.isatty', return_value=True):
                self.assertFalse(ConsoleFormatter.supports_color())

    def test_color_text(self):
        """Test text coloring."""
        # Mock supports_color to return True
        with patch.object(ConsoleFormatter, 'supports_color', return_value=True):
            colored = ConsoleFormatter.color_text("test", "red")
            self.assertEqual(colored, "\033[31mtest\033[0m")

        # Mock supports_color to return False
        with patch.object(ConsoleFormatter, 'supports_color', return_value=False):
            colored = ConsoleFormatter.color_text("test", "red")
            self.assertEqual(colored, "test")

    def test_format_unit_list(self):
        """Test formatting a list of units."""
        units = [
            UnitStatus(
                name="foo.service",
                load_state="loaded",
                active_state="active",
                sub_state="running",
                description="Foo Service",
                enabled=True
            ),
            UnitStatus(
                name="bar.service",
                load_state="loaded",
                active_state="inactive",
                sub_state="dead",
                description="Bar Service",
                enabled=False
            )
        ]

        # Mock supports_color to return False to make testing easier
        with patch.object(ConsoleFormatter, 'supports_color', return_value=False):
            # Mock color_text to return the text unchanged
            with patch.object(ConsoleFormatter, 'color_text',
                              side_effect=lambda text, color: text):
                result = ConsoleFormatter.format_unit_list(units)

                # Check that the result contains the unit names
                self.assertIn("foo.service", result)
                self.assertIn("bar.service", result)

                # Check that the result contains the states
                self.assertIn("loaded", result)
                self.assertIn("active", result)
                self.assertIn("inactive", result)
                self.assertIn("running", result)
                self.assertIn("dead", result)

                # Check that the result contains the descriptions
                self.assertIn("Foo Service", result)
                self.assertIn("Bar Service", result)

                # Check that the result contains the enabled status
                self.assertIn("yes", result)
                self.assertIn("no", result)

    def test_format_unit_status(self):
        """Test formatting detailed status of a unit."""
        unit = UnitStatus(
            name="foo.service",
            load_state="loaded",
            active_state="active",
            sub_state="running",
            description="Foo Service",
            enabled=True
        )

        # Mock supports_color to return False to make testing easier
        with patch.object(ConsoleFormatter, 'supports_color', return_value=False):
            # Mock color_text to return the text unchanged
            with patch.object(ConsoleFormatter, 'color_text',
                              side_effect=lambda text, color: text):
                result = ConsoleFormatter.format_unit_status(unit)

                # Check that the result contains the unit name
                self.assertIn("foo.service", result)

                # Check that the result contains the description
                self.assertIn("Foo Service", result)

                # Check that the result contains the states
                self.assertIn("loaded", result)
                self.assertIn("active", result)
                self.assertIn("running", result)

                # Check that the result contains the enabled status
                self.assertIn("enabled", result)