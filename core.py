
from core_module import CoreModule
from core_commands import CoreCommands
from attrdict import AttrDict

from typing import Optional, List, Dict


UNKNOWN_COMMAND_MSG = "Unknown command"


class Error(Exception):
  """Base error class."""


class InvalidModuleError(Error):
  """Invalid modules attempted to load."""


class Core:
  """This is the core of the framework."""

  def __init__(self, modules: Optional[List[CoreModule]] = None) -> None:
    """Initialize the core."""
    self.env = {}

    self.modules = AttrDict(none=None)
    self.module_initializers = self._get_initializers()
    self.prompt = ">>>"
    self._loaded_module = "none"
    self.aliases = {"print":"echo"}
    self._core_commands = CoreCommands()

    CORE_COMMANDS = {
        "echo": self._core_commands.echo,
      }

    if modules:
      self._load_modules(modules)

  def _load_modules(self, modules: List[CoreModule]) -> None:
      for module in modules:
        self._load_module(module)

  def load_aliases_from_file(self, filepath: str) -> bool:
    with open(filepath, 'r') as f:
      content = f.read()
    for line in content.split("\n"):
      if ":" in line:
        splitted = line.split(":")
        if not splitted:
          continue
        if not len(splitted) == 2:
          continue
        self._load_alias(splitted[0], splitted[1])

  def _load_alias(self, alias: str, command: str) -> None:
    self.aliases[alias] = command

  def _load_module(self, module: CoreModule = None) -> None:
    """Load a module."""
    if not self._is_valid_module(module):
      raise InvalidModuleError("Could not load module {module}".format(module=module))
    
    if module.name in self.modules.keys():
      raise AttemptedDoubleImport("Attempted to import a module with name {module} twice.".format(module=module.name))

    self.modules[module.name] = module(**self.module_initializers)

  def _is_valid_module(self, module: CoreModule) -> bool:
    if not issubclass(module, CoreModule):
      return False
    if not getattr(module, "name"):
      return False
    
    return True

  def _get_initializers(self) -> Dict:
    """Configuration data to pass to all modules."""
    return {"env": self.env}

  def bootstrap(self, *args: str) -> None:
    for arg in args:
      print(arg)

    self._loop()

  def _loop(self) -> None:
    while True:
      r = input(self._get_prompt())
      if not self._process_input(r):
        break
      

  def _process_input(self, r: str) -> bool:
    s = r.split()
    if not s:
      return True
    com = self._alias_check(s)
    args = s[1:]

    if com in self.EXIT_COMMANDS:
      self._exit()
    elif com in self.CORE_COMMANDS:
      self.CORE_COMMANDS[com](args)
    elif com in self.modules[self._loaded_module].COMMANDS:
      self._get_loaded_module().COMMANDS[com](args)
    else:
      print(UNKNOWN_COMMAND_MSG)
    return True

  def _get_loaded_module(self) -> CoreModule:
    return self.modules[self._loaded_module]

  def _exit(self) -> None:
    """Abstraction for future - cleaner exits."""
    exit()

  def _alias_check(self, s: str) -> str:
    """See if there is an alias registered for the command."""
    if s in self.aliases.keys():
      return self.aliases[s]
    return s

  def _get_prompt(self) -> str:
    return "{module}{prompt} ".format(module=self._loaded_module, prompt=self.prompt) 
      
