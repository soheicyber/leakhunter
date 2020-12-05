
from typing import Any, Dict

class ModuleCommand:

  def __init__(self, *args, **kwargs) -> Any:
    return "The result of running the command."

  @staticmethod
  def help(*args, **kwargs) -> str:
    return "A help message for this command."

class CoreModule:

  def __init__(self, env=None):
    self.core_env = env
    self.commands = {ModuleCommand.__name__: ModuleCommand}

  def get_commands(self) -> Dict[str, "ModuleCommand"]:
    """Return the dict of commands supported by this module."""
    return self.commands

  
