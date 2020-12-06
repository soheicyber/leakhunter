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
import argparse
import hashlib
import subprocess
import time
import sqlite3

SUPPORTED_GENERATORS=["docz"]

ALLOWLIST=["127.0.0.1"]

LOGDIR="log/"
LOGFILE="log.txt"
CAMPAIGNDIR="campaign"


class LeakHunter(CoreModule):
  """The module class, to be interpreted by the core framework."""

  def __init__(self, *args, **kwargs):
    super().__init__(None, [Help, CheckLaunch, AddTarget, ShowTargets, DeleteTarget])
    self.launched = False
    self.target_list = []

    if not os.path.exists(LOGDIR):
      os.system("mkdir -p {logdir}".format(logdir=LOGDIR))
    if not os.path.exists(os.path.join(LOGDIR, LOGFILE)):
      os.system("touch {logfile}".format(logfile=os.path.join(LOGDIR, LOGFILE)))
    if not os.path.exists(CAMPAIGNDIR):
      os.system("mkdir -p {campaign}".format(campaign=CAMPAIGN))


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
    for com, c in mod.get_commands().items():
    
      print("{command_name}: {help}".format(command_name=com, help=c.help()))
    print("--------")
    return

  @staticmethod
  def help(*args, **kwargs) -> str:
    return "The help method."


class CheckLaunch(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    print(mod.launched)

  @staticmethod
  def help(*args, **kwargs):
    return "CheckLaunch command indicates if a campaign is running."


class AddTarget(ModuleCommand):

  def __init__(self, mod, *args, **kwargs) -> None:
    target=" ".join(args)
    if not target:
      return 
    print("Adding target: {target}".format(target=target))
    mod.target_list.append(target)
    return 

  @staticmethod
  def help() -> str:
    return "Add a target to the list of targets."


class ShowTargets(ModuleCommand):
  
  def __init__(self, mod, *args, **kwargs) -> None:
    print("----------")
    for i in range(len(mod.target_list)):
      print("{id}: {target}".format(id=i, target=mod.target_list[i]))
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
    del mod.target_list[v]
    
    

def append_allowlist(allowlist):
	fi = open(allowlist, "r")
	data = fi.read()
	fi.close()
	for ip in data.split("\n"):
		ALLOWLIST.append(ip)

def embed(SOST, EMB):
	return SOST.replace("::ID", EMB)

def docz(FINA, SOST, EMB, NIM, CAMP, PATH):
	SOST = embed(SOST, EMB)
	SOST = SOST.replace("\\","").replace("&","\\&")
	if VERBOSE:
		print("Creating file for: %s" % NIM)
		print("Unique file id is: %s" % EMB)
		print("Connection string: %s" % SOST)
	
	out = subprocess.check_output("python "+PATH+" "+FINA+" "+SOST,shell=True)
	if VERBOSE:
		print(out)
	out1 = subprocess.check_output("mv ./output.docx campaign/"+str(CAMP)+"/"+str(NIM)+".docx", shell=True)

def alert(msg):
	print(msg)

	c = "[%s]" % CAMPAIGN

	fi=open(LOG, "a")
	fi.write(c + msg + "\n")
	fi.close()


def allowlist():
	global ALLOWLIST
	ALLOWLIST.append(raw_input("Enter IP to add: "))

def honeyfile():
	global HONEYFILE
	HONEYFILE = raw_input("Path to honeyfile: ")

def targetfile():
	global TARGETFILE
	TARGETFILE = raw_input("Path to targetfile: ")

def campaign():
	global CAMPAIGN
	CAMPAIGN = raw_input("Campaign name: ")

def monitor():
	if not check_launch(MON=True):
		return

	if MON_STRING.split(":")[0] == "honeybadger":
		while True:
			time.sleep(PAUSE)
			honeybadger()
			
	
	if MON_STRING.split(":")[0] == "sqlitebugserver":
		while True:
			time.sleep(PAUSE)
			sqlitebugserver()

	if MON_STRING.split(":")[0] == "webbugserver":
		while True:
			time.sleep(PAUSE)
			webbugserver()

	return

def log():
	global LOG
	LOG = raw_input("New Log File: ")

def parse_targets():
	fi = open(TARGETFILE, "r")
	data = fi.read()
	fi.close()

	temp = []


	for i in data.split("\n"):
		if len(i) < 1:
			continue

		h = hashlib.sha1(CAMPAIGN+i).hexdigest()

		temp.append(i + "::" + h)

	out = subprocess.check_output("touch campaign/%s/.read" % CAMPAIGN, shell=True)

	if not os.path.exists("campaign/%s" % CAMPAIGN):
		subprocess.check_output("mkdir campaign/%s" % CAMPAIGN, shell=True)
	fi = open("campaign/"+CAMPAIGN+"/MAPPING.txt", "w")
	fi.write("\n".join(temp))
	fi.close()

	return temp

def generate():
	if not check_launch():
		return
	
	if not os.path.exists("campaign/%s" % CAMPAIGN):
		subprocess.check_output("mkdir campaign/%s" % CAMPAIGN, shell=True)

	for pair in parse_targets():
		this_name, this_id=pair.split("::")
		this_name = this_name.strip().replace(" ","_")
		this_id=this_id.strip()
		docz(HONEYFILE, SOURCE_STRING, this_id, this_name, CAMPAIGN, BUILDER_STRING.split(":")[1])
	print("Generation complete...")
	print("Files saved to: %s/%s" % ( "campaign", CAMPAIGN ))
	return

def env():
	print("\n-- printing environment --\n")
	print("Campaign: %s" % CAMPAIGN)
	print("Targetfile: %s" % TARGETFILE)
	print("Honeyfile: %s" % HONEYFILE)
	print("Logfile: %s" % LOG)
	print("Buildstring: %s" % BUILDER_STRING)
	print("Sourcestring: %s" % SOURCE_STRING)
	print("Monstring: %s" % MON_STRING)
	
	print("Allowlist: %s" % ALLOWLIST)
	

###END COM FUNCTIONS


def parse_com(com):

	comMap = {
	"help":help,
	"allowlist":allowlist,
	"honeyfile":honeyfile,
	"targetfile":targetfile,
	"generate":generate,
	"campaign":campaign,
	"monitor":monitor,
	"log":log,
	"env":env,
	"exit":exit
	}

	if com in comMap.keys():
		return comMap[com]()
	else:
		print("Command not found")

if __name__=="__main__":
	initialize()

	parser = argparse.ArgumentParser()
	parser.add_argument("--no-mon", action="store_true", help="Disable monitor features")
	parser.add_argument("-v","--verbose", action="store_true", help="Prints more about what's happening.")
	parser.add_argument("--source-string",help="Specifies collection source")
	parser.add_argument("--mon-string",help="Specifies mon access")
	parser.add_argument("--build-string",help="Specifies builder tool")
	parser.add_argument("--honeyfile",help="Path to honeyfile.  The docx file to be used as bait.")
	parser.add_argument("--targetfile",help="Path to target file.  One name per line")
	parser.add_argument("--allowlist",help="Path to allowlist.  Internal IPs to ignore")
	parser.add_argument("--campaign",help="Campaign name")
	

	args = parser.parse_args()

	if args.mon_string:
		MON_STRING=args.mon_string

	if args.build_string:
		BUILDER_STRING=args.build_string

	if args.source_string:
		SOURCE_STRING=args.source_string

	if args.honeyfile:
		HONEYFILE=args.honeyfile

	if args.targetfile:
		TARGETFILE=args.targetfile

	if args.allowlist:
		append_allowlist(allowlist)

	if args.campaign:
		CAMPAIGN=args.campaign

	if args.verbose:
		VERBOSE=True

	if not args.no_mon and MON_STRING == None:
		print("Error: MON_STRING not set")
		print("Please modify script to set MON_STRING")
		print("Alternatively you can specify on command line")
		print("Use: --mon-string=\"<monstring>\"")
		print("Or, disable mon features with --no-mon")
		print("Exiting..")
		exit()

	if SOURCE_STRING == None:
		print("Error: SOURCE_STRING not set")
		print("Please modify script to set SOURCE_STRING")
		print("Alternatively you can specify on command line")
		print("Use: --source-string=\"<sourcestring>\"")
		print("Exiting..")
		exit()

	if BUILDER_STRING == None:
		print("Error: BUILDER_STRING not set")
		print("Please modify script to set BUILDER_STRING")
		print("Alternatively you can specify on command line")
		print("Use: --build-string=\"<buildstring>\"")
		print("Exiting..")
		exit()



	if not args.no_mon and MON_STRING.split(":")[0] not in SUPPORTED_COLLECTORS:
		print("Error: MON_STRING collector not supported")
		print("Supported collectors are:")
		for collector in SUPPORTED_COLLECTORS:
			print(collector)
		print("To disable monitor features run with --no-mon flag")
		print("Exiting..")
		exit()
	if BUILDER_STRING.split(":")[0] not in SUPPORTED_GENERATORS:
		print("Error: BUILDER_STRING builder not supported")
		print("Supported builders are:")
		for generator in SUPPORTED_GENERATORS:
			print(generator)
		print("Exiting..")
		exit()

	menu="""
	#######################################
	## MOLEHUNT V1.0 Promethean Info Sec ##
	#######################################
	"""

	welcome = """
	Welcome, for help type "help".
	"""

	print(menu)

	print(welcome)

	read_loop()
	
	
