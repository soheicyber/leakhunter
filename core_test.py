"""tests for core.py"""
import unittest
import builtins

from pyfakefs import fake_filesystem, mox3_stubout

from core import Core


class CoreTest(unittest.TestCase):
    """Tests for Core."""

    _FAKE_ALIAS_KEY = 'test'
    _FAKE_ALIAS_VALUE = 'tests'
    _FAKE_ALIAS_FILE = {'filename': 'fake_aliases',
                        'content': f'{_FAKE_ALIAS_KEY}: {_FAKE_ALIAS_VALUE}'}

    def setUp(self):
        self.core = Core()
        self.fake_file = fake_filesystem.FakeFilesystem()
        self.os_mod = fake_filesystem.FakeOsModule(self.fake_file)
        self.open = fake_filesystem.FakeFileOpen(self.fake_file)
        self.stubs = mox3_stubout.StubOutForTesting()
        self.stubs.smart_set(builtins, 'open', self.open)
        self.fake_file.create_file(
            self._FAKE_ALIAS_FILE['filename'], contents=self._FAKE_ALIAS_FILE['content'])

    def test_load_aliases_from_file(self):
        """test that we are able to load aliases from a fake file."""
        self.assertTrue(self.core.load_aliases_from_file(
            self._FAKE_ALIAS_FILE['filename']))
        self.assertEqual(
            self.core.aliases[self._FAKE_ALIAS_KEY], self._FAKE_ALIAS_VALUE)


if __name__ == '__main__':
    unittest.main()
