"""Tests for core_module.py"""

import unittest
import stringcase

from core_module import CoreModule, ModuleCommand


class CoreTest(unittest.TestCase):
    """Tests for CoreModule"""

    class FakeCommand(ModuleCommand):
        """Fake command used for testing."""

    def setUp(self):
        self.core_module = CoreModule()

    def test_get_commands(self):
        """Test the get_commands method returns as we expect."""
        self.assertEqual(
            self.core_module.get_commands(),
            {stringcase.snakecase(ModuleCommand.__name__): ModuleCommand}
        )

    def test_load_commands(self):
        """Test we are able to load commands via load_commands."""
        self.core_module.load_commands([self.FakeCommand])
        self.assertEqual(
            self.core_module.get_commands(),
            {
                stringcase.snakecase(ModuleCommand.__name__): ModuleCommand,
                stringcase.snakecase(self.FakeCommand.__name__): self.FakeCommand
            }
        )


if __name__ == '__main__':
    unittest.main()
