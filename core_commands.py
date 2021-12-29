"""The core commands to be used by default."""


class CoreCommands:
    """Core commands to be used by default."""

    def __init__(self):
        pass

    @staticmethod
    def echo(*args):
        """Echos back whatever is said to it."""
        print(args)

    @staticmethod
    def lower(*args):
        """returns the lowercase version of arguments."""
        return " ".join([i for i in args if isinstance(i, str)])
