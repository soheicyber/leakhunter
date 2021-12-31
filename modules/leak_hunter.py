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


import time
import shutil
import hashlib
import subprocess
import socket

from os import path, linesep, listdir, makedirs
from pathlib import Path as PathlibPath

import furl
from core_module import CoreModule, ModuleCommand


ALLOWLIST = []

DOCZ_PATH = "docz/docz.py"

DEFAULT_PORT = 5578
DEFAULT_ADDR = "127.0.0.1"

LOGDIR = "log/"
LOGFILE = "log.txt"
CAMPAIGNDIR = "campaign"
TEMPLATEDIR = "templates"


class NoListenAddrError(Exception):
    """No listen address has been set."""


class LeakHunter(CoreModule):
    """The module class, to be interpreted by the core framework."""

    def __init__(self, *args, **kwargs):
        del args
        del kwargs
        super().__init__(
            None,
            [
                Help,
                CheckLaunch,
                AddTarget,
                ShowTargets,
                DeleteTarget,
                SetCampaign,
                ShowCampaigns,
                DeleteCampaign,
                SetTargetFile,
                ShowTargetFile,
                ShowTemplateFiles,
                SetListenAddress,
                SetListenPort,
                ShowListenPort,
                ShowListenAddress,
                LaunchListener,
                LaunchInjection
            ]
        )
        self.launched = False
        self.campaign = None
        self.target_list = {}
        self.target_file = ""
        self.listen_addr = DEFAULT_ADDR
        self.listen_port = DEFAULT_PORT

        if not path.exists(LOGDIR):
            makedirs("{logdir}".format(logdir=LOGDIR), exist_ok=True)
        if not path.exists(path.join(LOGDIR, LOGFILE)):
            PathlibPath("{logfile}".format(
                logfile=path.join(LOGDIR, LOGFILE))
            ).touch()
        if not path.exists(CAMPAIGNDIR):
            makedirs("{campaign}".format(campaign=CAMPAIGNDIR), exist_ok=True)

    def save_campaign(self) -> None:
        """Save the state of a campaign."""
        if not self.campaign:
            return

        folder = path.join(CAMPAIGNDIR, self.campaign)
        if not path.exists(folder):
            makedirs("{campaign}/injected".format(campaign=folder),
                     exist_ok=True)

        target_list = path.join(CAMPAIGNDIR, self.campaign, "target_list")
        if not path.exists(target_list):
            PathlibPath("{target_list}".format(
                target_list=target_list)).touch()

        with open(target_list, "w") as open_file:
            for target, token in self.target_list.items():
                open_file.write(target + ":" + token + linesep)

        target_file = path.join(CAMPAIGNDIR, self.campaign, "target_file")
        listen_port_file = path.join(
            CAMPAIGNDIR, self.campaign, "listen_port_file")
        listen_addr_file = path.join(
            CAMPAIGNDIR, self.campaign, "listen_addr_file")
        if not path.exists(target_file):
            PathlibPath("{target_file}".format(
                target_file=target_file)).touch()
        if not path.exists(listen_port_file):
            PathlibPath("{listen_port_file}".format(
                listen_port_file=listen_port_file)).touch()
        if not path.exists(listen_addr_file):
            PathlibPath("touch", "{listen_addr_file}".format(
                listen_addr_file=listen_addr_file)).touch()

        with open(target_file, 'w') as open_file:
            open_file.write(str(self.target_file))

        with open(listen_port_file, 'w') as open_file:
            open_file.write(str(self.listen_port))

        with open(listen_addr_file, 'w') as open_file:
            open_file.write(self.listen_addr)

    def load_campaign(self) -> None:
        """Load a campaign from a saved file."""
        if not self.campaign:
            return

        folder = path.join(CAMPAIGNDIR, self.campaign)

        # Here we flush everything if this campaign doesn't exist.
        if not path.exists(folder):
            self.target_list = {}
            self.target_file = ""
            self.listen_port = DEFAULT_PORT
            self.listen_addr = DEFAULT_ADDR
            return

        target_list = path.join(CAMPAIGNDIR, self.campaign, "target_list")
        if not path.exists(target_list):
            return

        with open(target_list, "r") as f:
            self.target_list = {}
            data = f.read()
            for line in data.split(linesep):
                if line:
                    if not ":" in line:
                        raise Exception(
                            "Campaign created on old version of software, cannot import.")
                    target, token = line.split(":")
                    self.target_list[target] = token

        target_file = path.join(CAMPAIGNDIR, self.campaign, "target_file")
        listen_port_file = path.join(
            CAMPAIGNDIR, self.campaign, "listen_port_file")
        listen_addr_file = path.join(
            CAMPAIGNDIR, self.campaign, "listen_addr_file")
        if not path.exists(target_file) or not path.exists(listen_port_file) or not path.exists(listen_addr_file):
            return

        with open(target_file, "r") as f:
            self.target_file = f.read()

        with open(listen_port_file, "r") as f:
            try:
                self.listen_port = int(f.read())
            except ValueError:
                print(
                    "This campaign save has an invalid port value.\nSetting port to default.")
                self.listen_port = DEFAULT_PORT

        with open(listen_addr_file, "r") as f:
            self.listen_addr = f.read()

    def generate_token(self, target) -> None:
        """Create a token to use for identifying a target."""
        return hashlib.sha256((target + ":" + str(time.time())).encode()).hexdigest()

    def list_campaigns(self) -> None:
        """List the available campaigns."""
        campaigns = listdir(CAMPAIGNDIR)
        campaigns.sort()
        print("--------")
        for campaign in campaigns:
            print(campaign)
        print("--------")

    def delete_campaign(self, target) -> None:
        """Delete a campaign and associated files."""
        if self.campaign == target:
            print("Cannot delete currently loaded campaign")
            return

        folder = path.join(CAMPAIGNDIR, target)

        campaigns = listdir(CAMPAIGNDIR)
        if not target in campaigns:
            print("Unknown campaign")
            return

        shutil.rmtree(folder)

    def show_template_files(self) -> None:
        """Show all available files from the templates."""
        templates = listdir(TEMPLATEDIR)
        print("--------")
        for template in templates:
            print(template)
        print("--------")

    def set_target_file(self, target) -> None:
        """Set the template file to use."""
        templates = listdir(TEMPLATEDIR)
        if target not in templates:
            print("Target file must be from the list of templates..")
            self.show_template_files()
            return

        self.target_file = target

    def show_target_file(self) -> None:
        """Print the name of the selected template file."""
        print(self.target_file)

    def set_listen_port(self, port) -> None:
        """Set the port we will listen with."""
        self.listen_port = port

    def show_listen_port(self) -> None:
        """Show the port we will listen with."""
        print("{port}".format(port=self.listen_port))

    def set_listen_addr(self, addr) -> None:
        """Set the address we will listen on."""
        self.listen_addr = addr

    def show_listen_addr(self) -> None:
        """Show the address we will isten on."""
        print("{addr}".format(addr=self.listen_addr))

    def listen(self) -> None:
        """Start listening."""
        if not self.campaign:
            print("Must load a campaign first.")
            return

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not self.listen_addr:
                raise NoListenAddrError("No listen address set.")

            soc.bind((self.listen_addr, self.listen_port))
        except socket.error:
            print(
                "Unable to launch the listener, have you set the listen port and listen address?")
            return

        soc.listen(5)
        print("Listening for new connections on: {addr}:{port}\nCtrl-c to exit..".format(
            addr=self.listen_addr, port=self.listen_port))
        try:
            while True:
                conn, addr = soc.accept()
                if addr in ALLOWLIST:
                    continue

                data = conn.recv(1024)
                conn.close()

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
                    target=self.attribute_to_target(
                        furl.furl(args).args['target'].replace("'", "")))

                print(
                    "Connection from: {addr} -> {attribution}".format(
                        addr=addr, attribution=attribution))

        except KeyboardInterrupt:
            print("Stop listening...")
            return

    def get_url(self) -> str:
        """Return the URL of the listener."""
        return "http://{la}:{lp}/".format(la=self.listen_addr, lp=self.listen_port)

    def attribute_to_target(self, id: str) -> str:
        """Determine which target this id corresponds with."""
        # TODO reverse dictionary for speed with large numbers of lookups.
        for t, i in self.target_list.items():
            if i == id:
                return t
        return "Unknown"

    def inject(self) -> None:
        """Inject all the files needed to run a campaign as configured."""
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

        for target, target_id in self.target_list.items():
            target = target.strip().replace(" ", "_")
            target_id = target_id.strip()
            self.docz(self.target_file, self.get_url(), target_id, target)

        print("Injection complete...")
        print(
            "Files saved to: campaign/{campaign}/injected".format(campaign=self.campaign))
        return

    def docz(self, template_file: str, url: str, id_value: str, target: str) -> None:
        """This method calls the docz subprocess to edit a single file."""
        subprocess.call(
            ["python3 ",
             DOCZ_PATH,
             "-f",
             "templates/{template}".format(template=template_file),
             "-u",
             url,
             "-a",
             "leakhunter",
             " -t",
             str(id_value)])
        shutil.move(
            "./output.docx",
            "campaign/{campaign}/injected/{target}.docx".format(
                campaign=str(self.campaign),
                target=str(target)
            )
        )


###################################################
# Here are the commands available in this module. #
###################################################


class Help(ModuleCommand):
    """The help command."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if len(args) > 0 and args[0] in mod.get_commands().keys():
            print(mod.get_commands()[args[0]].help())
            return

        print("--------")
        buf = []
        for name, command in mod.get_commands().items():

            buf.append("{command_name}: {help}".format(
                command_name=name, help=command.help()))
        buf.sort()
        for line in buf:
            print(line)

        print("--------")
        return

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "The help method."


class SetCampaign(ModuleCommand):
    """Set what campaign you will use."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if len(args) != 1:
            print("Provide a campaign name as a single word.")
            return

        mod.save_campaign()
        mod.campaign = args[0]
        mod.append_prompt = mod.campaign
        mod.load_campaign()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Set the campaign you are running."


class ShowCampaigns(ModuleCommand):
    """Show all campaigns available."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if len(args) > 0:
            print("This command doesn't expect any arguments")
            return

        mod.list_campaigns()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "List all available campaigns"


class DeleteCampaign(ModuleCommand):
    """Delete a campaign and associated files."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if len(args) != 1:
            print("Please provide a campaign to remove")
            return

        mod.delete_campaign(args[0])

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Delete a campaign and all associated data."


class ShowTemplateFiles(ModuleCommand):
    """Show the template file list."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if len(args) > 0:
            print("Not expecting any args.")
            return

        mod.show_template_files()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "List the files available for use in a campaign."


class SetListenAddress(ModuleCommand):
    """Set the address we will listen on."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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
        mod.save_campaign()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Set the address we will call back to."


class ShowListenAddress(ModuleCommand):
    """Show the address we will listen on."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        mod.show_listen_addr()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Show the currently set address we will call back to."


class SetListenPort(ModuleCommand):
    """Set the port we will listen on."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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
        mod.save_campaign()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Set the port we will call back to."


class ShowListenPort(ModuleCommand):
    """Show the port we will listen on."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        mod.show_listen_port()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Show the currently set port we will call back to."


class SetTargetFile(ModuleCommand):
    """Set the target template file."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if len(args) != 1:
            print("Need a target file.")
            return

        mod.set_target_file(args[0])
        mod.save_campaign()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Set the target file for a campaign"


class ShowTargetFile(ModuleCommand):
    """Show the currently selected file."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if len(args) > 0:
            print("Not expecting any args.")
            return

        mod.show_target_file()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Show the currently selected file."


class CheckLaunch(ModuleCommand):
    """Check if a campaign is already listening."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print(mod.launched)

    @staticmethod
    def help(*args, **kwargs):
        return "CheckLaunch command indicates if a campaign is running."


class LaunchListener(ModuleCommand):
    """Launch the network listener."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if mod.launched:
            print("Listener appears to be running already?")
            return

        mod.listen()

    @staticmethod
    def help(*args, **kwargs):
        return "Launch the listener to wait for callbacks from our documents."


class LaunchInjection(ModuleCommand):
    """Inject the template into files ready to be distributed."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        mod.inject()

    @staticmethod
    def help(*args, **kwargs):
        return "Inject the web bug into the template document(s)."


class AddTarget(ModuleCommand):
    """Add a target to the target list."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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
    def help(*args, **kwargs) -> str:
        return "Add a target to the list of targets."


class ShowTargets(ModuleCommand):
    """Show the list of targets."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print("----------")
        for i in range(len(mod.target_list.keys())):
            print("{id}: {target}".format(
                id=i, target=list(mod.target_list.keys())[i]))
        print("----------")

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "The list of targets as currently loaded."


class DeleteTarget(ModuleCommand):
    """Delete a target from the list of targets."""

    def __init__(self, mod, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if len(args) == 0 or len(args) > 1:
            print(
                "Please provide a target id number from "
                "the list of targets (use command show_targets)")
            return
        try:
            id_val = int(args[0])
        except ValueError:
            print("Please provide a valid integer id")
            return

        print("Deleting id {v} from list of targets".format(v=id_val))
        del mod.target_list[mod.target_list.keys()[id_val]]
        mod.save_campaign()

    @staticmethod
    def help(*args, **kwargs) -> str:
        return "Delete a target from the list."

#######################
# End command section #
#######################
