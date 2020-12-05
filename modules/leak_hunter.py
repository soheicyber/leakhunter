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
import os
import argparse
import hashlib
import subprocess
import time
import sqlite3

SUPPORTED_GENERATORS=["docz"]

SUPPORTED_COLLECTORS=["honeybadger","webbugserver","sqlitebugserver"]

ALLOWLIST=["127.0.0.1"]

LOGDIR="logs/"
LOGFILE="log.txt"


def initialize():
	if not os.path.exists(LOG):
		os.system("touch %s" %LOG)
	if not os.path.exists("campaign"):
		os.system("mkdir campaign")


def check_launch(MON=False):
	if CAMPAIGN is None or TARGETFILE is None or HONEYFILE is None:
		return False

	if MON and MON_STRING is None:
		return False
	

	return True

def appendwhitelist(whitelist):
	fi = open(whitelist, "r")
	data = fi.read()
	fi.close()
	for ip in data.split("\n"):
		WHITELIST.append(ip)

def embed(SOST, EMB):
	return SOST.replace("::ID", EMB)

def docz(FINA, SOST, EMB, NIM, CAMP, PATH):
	SOST = embed(SOST, EMB)
	SOST = SOST.replace("\\","").replace("&","\\&")
	if VERBOSE:
		print "Creating file for: %s" % NIM
		print "Unique file id is: %s" % EMB
		print "Connection string: %s" % SOST
	
	out = subprocess.check_output("python "+PATH+" "+FINA+" "+SOST,shell=True)
	if VERBOSE:
		print out
	#out0 = subprocess.check_output("mkdir campaign/"+str(CAMP) ,shell=True)
	out1 = subprocess.check_output("mv ./output.docx campaign/"+str(CAMP)+"/"+str(NIM)+".docx", shell=True)

def read_loop():
	
	sub = ""	
	cc = ""
	if CAMPAIGN is not  None: 
		cc = CAMPAIGN
	while True:
		sub = parse_com(raw_input("%s>>> " % cc))

def webbugserver():
	(service, user, passwd, database) = MON_STRING.split(":")
	output = subprocess.check_output( "mysql -u %s --password='%s' -e 'select id, ip_address, time from requests' %s 2>/dev/null" % (user, passwd, database), shell=True)
        

	rows = []
	c = True
	for line in output.split("\n"):
		if c:
			c = False
			continue
		
		rows.append(line)
	
        data = ""

        try:
                fi = open("campaign/%s/.read" % CAMPAIGN, 'r')
                data = fi.read()
                fi.close()
        except:
                out = subprocess.check_output("touch campaign/%s/.read" % CAMPAIGN, shell=True)

        rread = data.split("\n")

        fi = open("campaign/%s/MAPPING.txt" % CAMPAIGN, "r")
        data = fi.read()
        fi.close()

        mapping = data.split("\n")
        ids = {}
        for line in mapping:
                ids[line.split("::")[1].strip()] = line.split("::")[0].strip()


        for row in rows:
		row=row.split("\t")
		if len(row) != 3:
			continue

		if str(row[2])+str(row[0]) in rread:
                        continue

                if row[0] in ids.keys() and not row[1] in WHITELIST:
                        alert("Callback Recieved For %s from %s at %s" % (ids[row[0]], row[1], row[2]))
                        fi = open("campaign/%s/.read" % CAMPAIGN, "a")
                        fi.write(str(row[2])+str(row[0]) + "\n")
                        fi.close()



def sqlitebugserver():	
	conn = sqlite3.connect(MON_STRING.split(":")[1])
        c = conn.cursor()

        data = ""

        try:
                fi = open("campaign/%s/.read" % CAMPAIGN, 'r')
                data = fi.read()
                fi.close()
        except:
                out = subprocess.check_output("touch campaign/%s/.read" % CAMPAIGN, shell=True)

        rread = data.split("\n")

        fi = open("campaign/%s/MAPPING.txt" % CAMPAIGN, "r")
        data = fi.read()
        fi.close()

        mapping = data.split("\n")
        ids = {}
        for line in mapping:
                ids[line.split("::")[1].strip()] = line.split("::")[0].strip()


        for row in c.execute("SELECT * FROM requests"):

                if str(row[4])+str(row[0]) in rread:
                        continue

                if row[0] in ids.keys() and not row[2] in WHITELIST:
                        alert("Callback Recieved For %s from %s at %s" % (ids[row[0]], row[2], row[4]))
                        fi = open("campaign/%s/.read" % CAMPAIGN, "a")
                        fi.write(str(row[4]) + str(row[0]) + "\n")
                        fi.close()


def honeybadger():
        conn = sqlite3.connect(MON_STRING.split(":")[1])
        c = conn.cursor()
	
	data = ""

	try:
        	fi = open("campaign/%s/.read" % CAMPAIGN, 'r')
        	data = fi.read()
        	fi.close()
	except:
		out = subprocess.check_output("touch campaign/%s/.read" % CAMPAIGN, shell=True)

        rread = data.split("\n")

        fi = open("campaign/%s/MAPPING.txt" % CAMPAIGN, "r")
        data = fi.read()
        fi.close()

        mapping = data.split("\n")
        ids = {}
        for line in mapping:
                ids[line.split("::")[1].strip()] = line.split("::")[0].strip()


        for row in c.execute("SELECT * FROM beacons"):

		if str(row[0]) in rread:
                        continue
                
		if row[2] in ids.keys() and not row[4] in WHITELIST:
                        alert("Callback Recieved For %s from %s at %s" % (ids[row[2]], row[4], row[1]))
                        fi = open("campaign/%s/.read" % CAMPAIGN, "a")
                        fi.write(str(row[0]) + "\n")
                        fi.close()



def alert(msg):
	print msg

	c = "[%s]" % CAMPAIGN

	fi=open(LOG, "a")
	fi.write(c + msg + "\n")
	fi.close()


###START COM FUNCTIONS

def help():
	print "---"
	print "help -> Show this help dialog"
	print "honeyfile -> Set honeyfile path"
	print "whitelist -> Append to whitelist with file at path"
	print "targetfile -> Set path to target file"
	print "generate -> Generate campaign"
	print "campaign -> Set campaign"
	print "monitor -> Start monitor service"
	print "log -> set log file"
	print "env -> list all settings"
	print "exit -> Leave"
	print "---"

	return 


def whitelist():
	global WHITELIST
	WHITELIST.append(raw_input("Enter IP to add: "))


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
	print "Generation complete..."
	print "Files saved to: %s/%s" % ( "campaign", CAMPAIGN )
	return

def env():
	print """
	-- printing environment --
	"""
	print "Campaign: %s" % CAMPAIGN
	print "Targetfile: %s" % TARGETFILE
	print "Honeyfile: %s" % HONEYFILE
	print "Logfile: %s" % LOG
	print "Buildstring: %s" % BUILDER_STRING
	print "Sourcestring: %s" % SOURCE_STRING
	print "Monstring: %s" % MON_STRING
	
	print "Whitelist: %s" % WHITELIST
	


###END COM FUNCTIONS




def parse_com(com):

	comMap = {
	"help":help,
	"whitelist":whitelist,
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
		print "Command not found"

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
	parser.add_argument("--whitelist",help="Path to whitelist.  Internal IPs to ignore")
	parser.add_argument("--campaign",help="Campaign name")
	

	args= parser.parse_args()

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

	if args.whitelist:
		appendwhitelist(whitelist)

	if args.campaign:
		CAMPAIGN=args.campaign

	if args.verbose:
		VERBOSE=True

	if not args.no_mon and MON_STRING == None:
		print "Error: MON_STRING not set"
		print "Please modify script to set MON_STRING"
		print "Alternatively you can specify on command line"
		print "Use: --mon-string=\"<monstring>\""
		print "Or, disable mon features with --no-mon"
		print "Exiting.."
		exit()

	if SOURCE_STRING == None:
		print "Error: SOURCE_STRING not set"
                print "Please modify script to set SOURCE_STRING"
		print "Alternatively you can specify on command line"
                print "Use: --source-string=\"<sourcestring>\""
                print "Exiting.."
                exit()

	if BUILDER_STRING == None:
		print "Error: BUILDER_STRING not set"
                print "Please modify script to set BUILDER_STRING"
                print "Alternatively you can specify on command line"
                print "Use: --build-string=\"<buildstring>\""
		print "Exiting.."
                exit()



	if not args.no_mon and MON_STRING.split(":")[0] not in SUPPORTED_COLLECTORS:
		print "Error: MON_STRING collector not supported"
		print "Supported collectors are:"
		for collector in SUPPORTED_COLLECTORS:
			print collector
		print "To disable monitor features run with --no-mon flag"
		print "Exiting.."
		exit()
	if BUILDER_STRING.split(":")[0] not in SUPPORTED_GENERATORS:
		print "Error: BUILDER_STRING builder not supported"
		print "Supported builders are:"
		for generator in SUPPORTED_GENERATORS:
			print generator
		print "Exiting.."
		exit()

	menu="""
	#######################################
	## MOLEHUNT V1.0 Promethean Info Sec ##
	#######################################
	"""

	welcome = """
	Welcome, for help type "help".
	"""

	print menu

	print welcome

	read_loop()
	
	
