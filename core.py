
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

    self.core_commands_map = {
        "echo": self._core_commands.echo,
      }
    
    self.exit_commands_list = [
      "exit",
      "quit", 
      "leave",
    ]

    if modules:
      self._load_modules(modules)

  def _load_modules(self, modules: List[CoreModule]) -> None:
    """Load the modules provided."""
    for module in modules:
      self._load_module(module)

    if len(modules) == 1: 
      self._loaded_module = modules[0].__name__

  def load_aliases_from_file(self, filepath: str) -> bool:
    """With a provided alias file, load all aliases."""
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
    """Add an alias to the list of aliases."""
    self.aliases[alias] = command

  def _load_module(self, module: CoreModule = None) -> None:
    """Load a module."""
    if not self._is_valid_module(module):
      raise InvalidModuleError("Could not load module {module}".format(module=module))
    
    if module.__name__ in self.modules.keys():
      raise AttemptedDoubleImport("Attempted to import a module with name {module} twice.".format(module=module.__name__))

    self.modules[module.__name__] = module(**self.module_initializers)

  def _is_valid_module(self, module: CoreModule) -> bool:
    """Determine if the module is valid."""
    if not issubclass(module, CoreModule):
      return False
    if not getattr(module, "__name__"):
      return False
    
    return True

  def _get_initializers(self) -> Dict:
    """Configuration data to pass to all modules."""
    return {"env": self.env}

  def bootstrap(self, *args: str) -> None:
    """Launch the loaded module(s)."""
    for arg in args:
      print(arg)

    self._loop()

  def _loop(self) -> None:
    """Loop to continually take input from the user."""
    while True:
      r = input(self._get_prompt())
      if not self._process_input(r):
        break
      

  def _process_input(self, r: str) -> bool:
    """Process the user's input and pass to internal functions."""
    s = r.split()
    if not s:
      return True
    com = self._alias_check(s[0])
    args = s[1:]
    print("DEBUG: ", args)

    if com in self.exit_commands_list:
      self._exit()
    elif com in self.core_commands_map.keys():
      self.core_commands_maps[com](*args)
    elif com in self.modules[self._loaded_module].get_commands().keys():
      self._get_loaded_module().get_commands()[com](*args)
    else:
      print(UNKNOWN_COMMAND_MSG)
    return True

  def _get_loaded_module(self) -> CoreModule:
    """Get the list of of loaded modules."""
    return self.modules[self._loaded_module]

  def _exit(self) -> None:
    """Abstraction for future - cleaner exits."""
    exit()

  def _alias_check(self, s: str) -> str:
    """See if there is an alias registered for the command."""
    return self.aliases.get(s, s)

  def _get_prompt(self) -> str:
    return "{module}{prompt} ".format(module=self._loaded_module, prompt=self.prompt) 
      
