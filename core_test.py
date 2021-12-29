import unittest
import builtins
import mock

from core import Core
from pyfakefs import fake_filesystem, mox3_stubout

class CoreTest(unittest.TestCase):

  _FAKE_ALIAS_KEY = 'test'
  _FAKE_ALIAS_VALUE = 'tests'
  _FAKE_ALIAS_FILE = {'filename':'fake_aliases', 'content':'{key}: {value}'.format(key=_FAKE_ALIAS_KEY,value=_FAKE_ALIAS_VALUE)}

  def setUp(self):
    self.c = Core()
    self.fs = fake_filesystem.FakeFilesystem()
    self.os = fake_filesystem.FakeOsModule(self.fs)
    self.open = fake_filesystem.FakeFileOpen(self.fs)
    self.stubs = mox3_stubout.StubOutForTesting()
    self.stubs.smart_set(builtins, 'open', self.open)
    self.fs.create_file(self._FAKE_ALIAS_FILE['filename'], contents=self._FAKE_ALIAS_FILE['content'])


  def test_load_aliases_from_file(self):
    self.assertFalse(self.c.load_aliases_from_file(self._FAKE_ALIAS_FILE['filename'])) 
    self.assertEqual(self.c.aliases[self._FAKE_ALIAS_KEY], self._FAKE_ALIAS_VALUE)


if __name__ == '__main__':
  unittest.main()

