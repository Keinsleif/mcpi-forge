#!/usr/bin/python3

import os, sys, re, json, threading, queue
from multiprocessing import Value
from mcpi import minecraft
from importlib import import_module

print("Welcome to Minecraft Pi Forge.")
root=os.path.dirname(os.path.abspath(__file__))
conf_path=os.path.join(root,"conf","main.json")
if not os.path.isfile(conf_path):
	with open(conf_path,"w") as f:
		f.write("{}")

HELP_MSG="""Commands:
help			show this message
list			show available mods
list-enabled	show enabled mods
enable MOD		enable mod
disable MOD		disable mod
start MOD		start mod
stop MOD		stop mod
exit			exit mcpi-forge"""

def main():
	mod_list=os.listdir(root+"/mods/")
	for mod in mod_list:
		if not os.path.isdir(root+"/mods/"+mod):
			mod_list.remove(mod)
	with open(conf_path,"r") as f:
		main_conf=json.load(f)
	
	mod_enabled=main_conf.get("enabled",[])

	try:
		mc=minecraft.Minecraft.create()
	except:
		print("Unable to connect Minecraft.")
		sys.exit(1)
	re1=re.compile(r"enable .+")
	re2=re.compile(r"disable .+")
	re3=re.compile(r"start .+")
	re4=re.compile(r"stop .+")
	lists={'module':{},'state':{},'thread':{}}

	running=[]

	for m in mod_enabled:
		lists['module'][m]=import_module("mods."+m+".main")
		lists['state'][m]=Value("i",1)
		lists['thread'][m]=threading.Thread(target=lists['module'][m].main,args=(mc,lists['state'][m]))
		lists['thread'][m].start()
		running.append(m)

	print(str(len(mod_list))+" mods are loaded.")
	print(str(len(mod_enabled))+" mods are started.")

	while True:
		try:
			cmd=input("> ")
		except (KeyboardInterrupt,EOFError):
			cmd="exit"

		if cmd=="exit":
			print("Stopping all launched mods...")
			for i in running:
				lists['state'][i].value=0
			[lists['thread'][i].join() for i in running]
			main_conf["enabled"]=mod_enabled
			with open(conf_path,"w") as f:
				json.dump(main_conf,f,indent=4)
			break

		elif cmd=="help":
			print(HELP_MSG)

		elif cmd=="list":
			print("Installed Mods:")
			[print(i) for i in mod_list]
		elif cmd=="list-enabled":
			print("Enabled Mods:")
			[print(i) for i in mod_enabled]

		elif re1.match(cmd):
			mod=re1.match(cmd).group().replace("enable ","")
			if mod in mod_list:
				if not mod in mod_enabled:
					mod_enabled.append(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

		elif re2.match(cmd):
			mod=re2.match(cmd).group().replace("disable ","")
			if mod in mod_list:
				if mod in mod_enabled:
					mod_enabled.remove(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

		elif re3.match(cmd):
			mod=re3.match(cmd).group().replace("start ","")
			if mod in mod_list:
				if not mod in running:
					lists['module'][mod]=import_module("mods."+mod+".main")
					lists['state'][mod]=Value("i",1)
					lists['thread'][mod]=threading.Thread(target=lists['module'][mod].main,args=(mc,lists['state'][mod]))
					lists['thread'][mod].start()
					running.append(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

		elif re4.match(cmd):
			mod=re4.match(cmd).group().replace("stop ","")
			if mod in mod_list:
				if mod in running:
					lists['state'][mod].value=0
					running.remove(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

	sys.exit()


if __name__=="__main__":
	main()
