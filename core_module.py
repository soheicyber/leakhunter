

class CoreModule:

  def __init__(self, env=None):
    self.core_env = env
    self.commands = {"pass":lambda a : a}

  def get_commands(self) -> dict:
    """Return the dict of commands supported by this module."""
    return self.commands
  


  
