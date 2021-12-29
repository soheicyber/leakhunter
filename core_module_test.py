import unittest
import mock
import stringcase

from core_module import CoreModule, ModuleCommand

class CoreTest(unittest.TestCase):

  class FakeCommand(ModuleCommand):
    def __init__(self):
      super()

  def setUp(self):
    self.c = CoreModule()


  def test_get_commands(self):
    self.assertEqual(self.c.get_commands(), {stringcase.snakecase(ModuleCommand.__name__): ModuleCommand}) 
	
  def test_load_commands(self):
    
    self.c.load_commands([self.FakeCommand])
    self.assertEqual(self.c.get_commands(), {stringcase.snakecase(ModuleCommand.__name__): ModuleCommand, stringcase.snakecase(self.FakeCommand.__name__): self.FakeCommand})
    
    

if __name__ == '__main__':
  unittest.main()

