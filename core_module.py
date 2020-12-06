
import stringcase

from typing import Any, Dict, List

class ModuleCommand:

  def __init__(self, *args, **kwargs) -> Any:
    return "The result of running the command."

  @staticmethod
  def help(*args, **kwargs) -> str:
    return "A help message for this command."

class CoreModule:

  def __init__(self, env=None, commands: List = [ModuleCommand]):
    self.core_env = env
    self.commands = {}
    self.append_prompt = None
    self.load_commands(commands)

  def get_commands(self) -> Dict[str, "ModuleCommand"]:
    """Return the dict of commands supported by this module."""
    return self.commands

  def load_commands(self, commands: List) -> None:
    for command in commands:
      self.commands[stringcase.snakecase(command.__name__)] = command

  
