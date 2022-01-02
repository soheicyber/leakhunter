"""Core of the framework."""
from typing import Optional, List, Dict
import sys

from attrdict import AttrDict

from core_module import CoreModule
from core_commands import CoreCommands


UNKNOWN_COMMAND_MSG = "Unknown command"


class Error(Exception):
    """Base error class."""


class InvalidModuleError(Error):
    """Invalid modules attempted to load."""


class AttemptedDoubleImport(Error):
    """If a module was attempted to be loaded again."""


class Core:
    """This is the core of the framework."""

    # pylint: disable=too-many-instance-attributes
    # We want to track all of these items.

    def __init__(self, modules: Optional[List[CoreModule]] = None) -> None:
        """Initialize the core."""
        self.env = {}

        self.modules = AttrDict(none=None)
        self.module_initializers = self._get_initializers()
        self.prompt = ">>>"
        self._loaded_module = "none"
        self.aliases = {"print": "echo"}
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
        added_alias = False
        with open(filepath, 'r', encoding='utf-8') as working_file:
            content = working_file.read()
        for line in content.split("\n"):
            if ":" in line:
                splitted = line.split(":")
                if not splitted:
                    continue
                if not len(splitted) == 2:
                    continue
                self._load_alias(splitted[0], splitted[1])
                added_alias = True

        return added_alias

    def _load_alias(self, alias: str, command: str) -> None:
        """Add an alias to the list of aliases."""
        self.aliases[alias.strip()] = command.strip()

    def _load_module(self, module: CoreModule = None) -> None:
        """Load a module."""
        if not self._is_valid_module(module):
            raise InvalidModuleError(
                f"Could not load module {module}")

        if module.__name__ in self.modules.keys():
            raise AttemptedDoubleImport(
                f"Attempted to import a module with name {module.__name__} twice.")

        self.modules[module.__name__] = module(**self.module_initializers)

    @staticmethod
    def _is_valid_module(module: CoreModule) -> bool:
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
        try:
            while True:
                if not self._process_input(input(self._get_prompt())):
                    break
        except KeyboardInterrupt:
            print("\nExiting..")
            return

    def _process_input(self, inp: str) -> bool:
        """Process the user's input and pass to internal functions."""
        spl = inp.split()
        if not spl:
            return True
        com = self._alias_check(spl[0])
        args = spl[1:]

        if com in self.exit_commands_list:
            self._exit()
        elif com in self.core_commands_map:
            self.core_commands_map[com](*args)
        elif com in self.modules[self._loaded_module].get_commands().keys():
            self._get_loaded_module().get_commands()[com](
                self._get_loaded_module(), *args)
        else:
            print(UNKNOWN_COMMAND_MSG)
        return True

    def _get_loaded_module(self) -> CoreModule:
        """Get the list of of loaded modules."""
        return self.modules[self._loaded_module]

    @staticmethod
    def _exit(code: int = 0) -> None:
        """Abstraction for future - cleaner exits."""
        sys.exit(code)

    def _alias_check(self, process: str) -> str:
        """See if there is an alias registered for the command."""
        return self.aliases.get(process, process)

    def _get_prompt(self) -> str:
        if not (self._get_loaded_module().append_prompt
                and not isinstance(self._get_loaded_module().append_prompt, str)):
            return f"{self._loaded_module}{self.prompt} "
        return f"{self._loaded_module}-{self._get_loaded_module().append_prompt}{self.prompt}"
