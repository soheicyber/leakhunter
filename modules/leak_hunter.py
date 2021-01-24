#!/usr/bin/env python3

"""
Leak Hunter helps you to figure out who is leaking your confidential information.

You may use Leak Hunter to embed hidden web bugs into a number of documents.
Each document looks the same, but each document contains a different webbug ID.
The web bugs will phone home to a server which collects IP information.  This
way you can see which document has been leaked, and is phoning home from outside
your organization.

You should keep track of which webbug ID corresponds to which person, that way
you know who leaked the document.
"""

from core_module import CoreModule, ModuleCommand

import os
import time
import shutil
import argparse
import hashlib
import subprocess
import time
import sqlite3
import socket
import furl

ALLOWLIST = []

DOCZ_PATH = "docz/docz.py"

DEFAULT_PORT = 5578
DEFAULT_ADDR = "0.0.0.0"

LOGDIR = "log/"
LOGFILE = "log.txt"
CAMPAIGNDIR = "campaign"
TEMPLATEDIR = "templates"


class LeakHunter(CoreModule):
  """The module class, to be interpreted by the core framework."""

  def __init__(self, *args, **kwargs):
    super().__init__(None, [Help, CheckLaunch, AddTarget, ShowTargets, DeleteTarget, SetCampaign, ShowCampaigns, DeleteCampaign,
                            SetTargetFile, ShowTargetFile, ShowTemplateFiles, SetListenAddress, SetListenPort, ShowListenPort, ShowListenAddress, LaunchListener, LaunchInjection])
    self.launched = False
    self.campaign = None
    self.target_list = {}
    self.target_file = ""
    self.listen_addr = DEFAULT_ADDR
    self.listen_port = DEFAULT_PORT

    if not os.path.exists(LOGDIR):
      os.system("mkdir -p {logdir}".format(logdir=LOGDIR))
    if not os.path.exists(os.path.join(LOGDIR, LOGFILE)):
      os.system("touch {logfile}".format(
          logfile=os.path.join(LOGDIR, LOGFILE)))
    if not os.path.exists(CAMPAIGNDIR):
      os.system("mkdir -p {campaign}".format(campaign=CAMPAIGNDIR))

  def save_campaign(self) -> None:
    if not self.campaign:
      return

    folder = os.path.join(CAMPAIGNDIR, self.campaign)
    if not os.path.exists(folder):
      os.system("mkdir -p {campaign}/injected".format(campaign=folder))

    target_list = os.path.join(CAMPAIGNDIR, self.campaign, "target_list")
    if not os.path.exists(target_list):
      os.system("touch {target_list}".format(target_list=target_list))

    with open(target_list, "w") as f:
      for target, token in self.target_list.items():
        f.write(target + ":" + token + os.linesep)

    target_file = os.path.join(CAMPAIGNDIR, self.campaign, "target_file")
    if not os.path.exists(target_file):
      os.system("touch {target_file}".format(target_file=target_file))

    with open(target_file, "w") as f:
      f.write(self.target_file)

    listen_port_file = os.path.join(
        CAMPAIGNDIR, self.campaign, "listen_port_file")
    listen_addr_file = os.path.join(
        CAMPAIGNDIR, self.campaign, "listen_addr_file")
    if not os.path.exists(listen_port_file):
      os.system("touch {listen_port_file}".format(
          listen_port_file=listen_port_file))

    if not os.path.exists(listen_addr_file):
      os.system("touch {listen_addr_file}".format(
          listen_addr_file=listen_addr_file))

    with open(listen_port_file, 'w') as f:
      f.write(str(self.listen_port))

    with open(listen_addr_file, 'w') as f:
      f.write(self.listen_addr)

  def load_campaign(self) -> None:
    if not self.campaign:
      return

    folder = os.path.join(CAMPAIGNDIR, self.campaign)

    # Here we flush everything if this campaign doesn't exist.
    if not os.path.exists(folder):
      self.target_list = {}
      self.target_file = ""
      self.listen_port = DEFAULT_PORT
      self.listen_addr = DEFAULT_ADDR
      return

    target_list = os.path.join(CAMPAIGNDIR, self.campaign, "target_list")
    if not os.path.exists(target_list):
      return

    with open(target_list, "r") as f:
      self.target_list = {}
      data = f.read()
      for line in data.split(os.linesep):
        if line:
          if not ":" in line:
            raise Exception(
                "Campaign created on old version of software, cannot import.")
          target, token = line.split(":")
          self.target_list[target] = token

    target_file = os.path.join(CAMPAIGNDIR, self.campaign, "target_file")
    listen_port_file = os.path.join(
        CAMPAIGNDIR, self.campaign, "listen_port_file")
    listen_addr_file = os.path.join(
        CAMPAIGNDIR, self.campaign, "listen_addr_file")
    if not os.path.exists(target_file) or not os.path.exists(listen_port_file) or not os.path.exists(listen_addr_file):
      return

    with open(target_file, "r") as f:
      self.target_file = f.read()

    with open(listen_port_file, "r") as f:
      try:
        self.listen_port = int(f.read())
      except ValueError:
        print("This campaign save has an invalid port value.\nSetting port to default.")
        self.listen_port = DEFAULT_PORT

    with open(listen_addr_file, "r") as f:
      self.listen_addr = f.read()

  def generate_token(self, target) -> None:
    return hashlib.sha256((target + ":" + str(time.time())).encode()).hexdigest()

  def list_campaigns(self) -> None:
    campaigns = os.listdir(CAMPAIGNDIR)
    campaigns.sort()
    print("--------")
    for campaign in campaigns:
      print(campaign)
    print("--------")

  def delete_campaign(self, target) -> None:
    if self.campaign == target:
      print("Cannot delete currently loaded campaign")
      return

    folder = os.path.join(CAMPAIGNDIR, target)

    campaigns = os.listdir(CAMPAIGNDIR)
    if not target in campaigns:
      print("Unknown campaign")
      return

    shutil.rmtree(folder)

  def show_template_files(self) -> None:
    templates = os.listdir(TEMPLATEDIR)
    print("--------")
    for f in templates:
      print(f)
    print("--------")

  def set_target_file(self, target) -> None:
    templates = os.listdir(TEMPLATEDIR)
    if target not in templates:
      print("Target file must be from the list of templates..")
      self.show_template_files()
      return

    self.target_file = target

  def show_target_file(self) -> None:
    print(self.target_file)

  def set_listen_port(self, port) -> None:
    self.listen_port = port

  def show_listen_port(self) -> None:
    print("{port}".format(port=self.listen_port))

  def set_listen_addr(self, addr) -> None:
    self.listen_addr = addr

  def show_listen_addr(self) -> None:
    print("{addr}".format(addr=self.listen_addr))

  def listen(self) -> None:
    if not self.campaign:
      print("Must load a campaign first.")
      return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      addr = '0.0.0.0'
      if self.listen_addr != '':
        addr = self.listen_addr

      s.bind((addr, self.listen_port))
    except socket.error:
      print("Unable to launch the listener, have you set the listen port and listen address?")
      return

    s.listen(5)
    print("Listening for new connections on: {addr}:{port}\nCtrl-c to exit..".format(
        addr=addr, port=self.listen_port))
    try:
      while True:
        c, addr = s.accept()
        if addr in ALLOWLIST:
          continue

        data = c.recv(1024)
        c.close()

        verb = None
        args = None
        try:
          lines = data.split(b"\r\n")
          req = lines[0]
          verb, args, _ = req.split()
        except IndexError:
          attribution = "Unable to parse"

        if verb and args:
          if verb not in [b"GET"]:
            attribution = "Unable to parse"

        # TODO Add agent checking to reduce noise.
        attribution = "Attributed to {target}".format(
            target=self.attribute_to_target(furl.furl(args).args['target'].replace("'", "")))

        print(
            "Connection from: {addr} -> {attribution}".format(addr=addr, attribution=attribution))

    except KeyboardInterrupt:
      print("Stop listening...")
      return

  def get_url(self) -> str:
    return "http://{la}:{lp}/".format(la=self.listen_addr, lp=self.listen_port)

  def attribute_to_target(self, id: str) -> str:
    # TODO reverse dictionary for speed with large numbers of lookups.
    for t, i in self.target_list.items():
      if i == id:
        return t
    return "Unknown"

  def inject(self) -> None:
    if not self.campaign:
      print("Must load a campaign first.")
      return

    if not self.target_file:
      print("We need a target file before we can inject into it.")
      print("Please set with set_target_file")
      return

    if not self.listen_addr or not self.listen_port:
      print("We need a listen address and port, please set both first.")
      return

    if not self.target_list:
      print("Please add some targets first...")
      return

    for target, id in self.target_list.items():
      target = target.strip().replace(" ", "_")
      id = id.strip()
      self.docz(self.target_file, self.get_url(), id, target,
                self.campaign)

    print("Injection complete...")
    print(
        "Files saved to: campaign/{campaign}/injected".format(campaign=self.campaign))
    return

  def docz(self, template_file, url, id, target, campaign):

    out = subprocess.check_output(
        "python3 " + DOCZ_PATH + " -f templates/" + template_file + " -u " + url + " -a leakhunter" + " -t" + str(id), shell=True)
    out1 = subprocess.check_output(
        "mv -f ./output.docx campaign/" + str(self.campaign) + "/injected/" + str(target) + ".docx", shell=True)


###################################################
# Here are the commands available in this module. #
###################################################


class Help(ModuleCommand):
  """The help command."""

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) > 0 and args[0] in mod.get_commands().keys():
      print(mod.get_commands()[args[0]].help())
      return

    print("--------")
    buf = []
    for com, c in mod.get_commands().items():

      buf.append("{command_name}: {help}".format(
          command_name=com, help=c.help()))
    buf.sort()
    for line in buf:
      print(line)

    print("--------")
    return

  @staticmethod
  def help(*args, **kwargs) -> str:
    return "The help method."


class SetCampaign(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) != 1:
      print("Provide a campaign name as a single word.")
      return

    mod.campaign = args[0]
    mod.append_prompt = mod.campaign
    mod.load_campaign()
    mod.save_campaign()

  @staticmethod
  def help() -> str:
    return "Set the campaign you are running."


class ShowCampaigns(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) > 0:
      print("This command doesn't expect any arguments")
      return

    mod.list_campaigns()

  @staticmethod
  def help() -> str:
    return "List all available campaigns"


class DeleteCampaign(ModuleCommand):

  def __init__(self, mod, *args, **kwaergs) -> None:
    if len(args) != 1:
      print("Please provide a campaign to remove")
      return

    mod.delete_campaign(args[0])

  @staticmethod
  def help() -> str:
    return "Delete a campaign and all associated data."


class ShowTemplateFiles(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) > 0:
      print("Not expecting any args.")
      return

    mod.show_template_files()

  @staticmethod
  def help() -> str:
    return "List the files available for use in a campaign."


class SetListenAddress(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) != 1:
      print("Please provide the IP address to route back to this machine.")
      return

    addr = args[0]

    try:
      socket.inet_aton(addr)
    except socket.error:
      print("Please provide a valid IP address.")
      return

    mod.set_listen_addr(addr)

  @staticmethod
  def help() -> str:
    return "Set the address we will call back to."


class ShowListenAddress(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    mod.show_listen_addr()

  @staticmethod
  def help() -> str:
    return "Show the currently set address we will call back to."


class SetListenPort(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) != 1:
      print("Please provide a port.")
      return

    try:
      port = int(args[0])
    except ValueError:
      print("Please provide an integer value")
      return

    if port < 0 or port > 65535:
      print("Please provide a value in the range 0 < i < 65536")
      return

    mod.set_listen_port(port)

  @staticmethod
  def help() -> str:
    return "Set the port we will call back to."


class ShowListenPort(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    mod.show_listen_port()

  @staticmethod
  def help() -> str:
    return "Show the currently set port we will call back to."


class SetTargetFile(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) != 1:
      print("Need a target file.")
      return

    mod.set_target_file(args[0])

  @staticmethod
  def help() -> str:
    return "Set the target file for a campaign"


class ShowTargetFile(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) > 0:
      print("Not expecting any args.")
      return

    mod.show_target_file()

  @staticmethod
  def help() -> str:
    return "Show the currently selected file."


class CheckLaunch(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    print(mod.launched)

  @staticmethod
  def help(*args, **kwargs):
    return "CheckLaunch command indicates if a campaign is running."


class LaunchListener(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if mod.launched:
      print("Listener appears to be running already?")
      return

    mod.listen()

  @staticmethod
  def help(*args, **kwargs):
    return "Launch the listener to wait for callbacks from our documents."


class LaunchInjection(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    mod.inject()

  @staticmethod
  def help(*args, **kwargs):
    return "Inject the web bug into the template document(s)."


class AddTarget(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    target = " ".join(args)
    if not target:
      return
    print("Adding target: {target}".format(target=target))
    if target in mod.target_list.keys():
      print("Target already in list.")
      return

    if ":" in target:
      print("Cannot add target with ':' character")
      return

    mod.target_list[target] = mod.generate_token(target)
    mod.save_campaign()
    return

  @staticmethod
  def help() -> str:
    return "Add a target to the list of targets."


class ShowTargets(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    print("----------")
    for i in range(len(mod.target_list.keys())):
      print("{id}: {target}".format(
          id=i, target=list(mod.target_list.keys())[i]))
    print("----------")

  @staticmethod
  def help() -> str:
    return "The list of targets as currently loaded."


class DeleteTarget(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    if len(args) == 0 or len(args) > 1:
      print("Please provide a target id number from the list of targets (use command show_targets)")
      return
    try:
      v = int(args[0])
    except ValueError:
      print("Please provide a valid integer id")
      return

    print("Deleting id {v} from list of targets".format(v=v))
    del mod.target_list[mod.target_list.keys()[v]]
    mod.save_campaign()

#######################
# End command section #
#######################
