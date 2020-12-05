
from core import Core
from modules.leak_hunter import LeakHunter

import argparse

BANNER = """#######################################
## LeakHunter V1.0 from Sohei Cyber  ##
#######################################\n"""

WELCOME_MSG = "Welcome, for help type \"help\"."


def main():
  """Initialize the framework."""
  core=Core(modules=[LeakHunter])

  parser = argparse.ArgumentParser()
  parser.add_argument("-v","--verbose", action="store_true", help="Prints more about what's happening.")
  parser.add_argument("--honeyfile",help="Path to honeyfile.  The docx file to be used as bait.")
  parser.add_argument("--targetfile",help="Path to target file.  One name per line")
  parser.add_argument("--allowlist",help="Path to allowlist file.  Internal IPs to ignore")
  parser.add_argument("--campaign",help="Campaign name")


  args=parser.parse_args()

  if args.honeyfile:
    core.modules.leak_hunter.honeyfile=args.honeyfile

  if args.targetfile:
    core.modules.leak_hunter.targetfile=args.targetfile

  if args.allowlist:
    core.modules.leak_hunter.allowlist=args.allowlist

  if args.campaign:
    core.modules.leak_hunter.campaign=args.campaign

  if args.verbose:
    core.verbose=True

  core.bootstrap(BANNER, WELCOME_MSG)

if __name__ == "__main__":
  main()
