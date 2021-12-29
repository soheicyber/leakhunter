"""The core module of LeakHunter."""

from typing import Any, Dict, List
import stringcase


class ModuleCommand:
    """The base class for a module."""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.result = []

    @staticmethod
    def help(*args, **kwargs) -> str:
        """Provides help for the command."""
        return "A help message for this command."

    def run(self, *args, **kwargs) -> Any:
        """Process and returns the results of the command."""

        if self.result:
            return self.result
        return "The result of running this command."


class CoreModule:
    """The core module from which the framework is built."""

    def __init__(self, env=None, commands: List = None):
        if not commands:
            commands = [ModuleCommand]
        self.core_env = env
        self.commands = {}
        self.append_prompt = None
        self.load_commands(commands)

    def get_commands(self) -> Dict[str, "ModuleCommand"]:
        """Return the dict of commands supported by this module."""
        return self.commands

    def load_commands(self, commands: List) -> None:
        """Load any new command(s) into the module."""
        for command in commands:
            self.commands[stringcase.snakecase(command.__name__)] = command
