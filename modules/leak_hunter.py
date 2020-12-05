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

LOGDIR="logs/"
LOGFILE="log.txt"

class LeakHunter(CoreModule):

  def __init__(self, *args, **kwargs):
    self.launched = False

  def initialize(self):
    if not os.path.exists(LOG):
      os.system("touch %s" %LOG)
    if not os.path.exists("campaign"):
      os.system("mkdir campaign")

  def get_commands(self) -> dict:
    return {"help": self.help, CheckLaunch.__name__: CheckLaunch}

  def help(self, *args, **kwargs) -> None:
    if len(args) > 0 and args[0] in self.get_commands().keys():
      print(self.get_commands()[args[0]].help())
      return  

    print("---")
    print("help -> Show this help dialog")
    print("honeyfile -> Set honeyfile path")
    print("allowlist -> Append to allowlist with file at path")
    print("targetfile -> Set path to target file")
    print("generate -> Generate campaign")
    print("campaign -> Set campaign")
    print("monitor -> Start monitor service")
    print("log -> set log file")
    print("env -> list all settings")
    print("exit -> Leave")
    print("---")
    return

class CheckLaunch(ModuleCommand):

  def __init__(self, mod, *args, **kwargs):
    return mod.launched

  @staticmethod
  def help(*args, **kwargs):
    return "CheckLaunch command indicates if a campaign is running."

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
	
	
