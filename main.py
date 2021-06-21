#!/usr/bin/python3

import os, sys, re, json, threading, queue
from mcpi import minecraft
from importlib import import_module

print("Welcome to Minecraft Pi Forge.")
root=os.path.dirname(os.path.abspath(__file__))

def main():
	mod_list=os.listdir(root+"/mods/")
	for mod in mod_list:
		if not os.path.isdir(root+"/mods/"+mod):
			mod_list.remove(mod)
	with open(root+"/conf/mods.json") as f:
		mod_conf=json.load(f)
	
#	mod_enabled=os.listdir(root+"/conf/enabled/")
	mod_enabled=mod_conf["enabled"]

	try:
		mc=minecraft.Minecraft.create()
	except:
		print("Unable to connect Minecraft.")
		sys.exit(1)
	re1=re.compile(r"enable .+")
	re2=re.compile(r"disable .+")
	re3=re.compile(r"start .+")
	re4=re.compile(r"stop .+")
	lists={'module':{},'queue':{},'thread':{}}

	running=[]

	for m in mod_enabled:
		lists['module'][m]=import_module("mods."+m+".main")
		lists['queue'][m]=queue.Queue()
		lists['queue'][m].put(1)
		lists['thread'][m]=threading.Thread(target=lists['module'][m].main,args=(mc,lists['queue'][m]))
		lists['thread'][m].start()
		running.append(m)

	print(len(mod_enabled)+" mods are loaded.")

	while True:
		try:
			cmd=input("> ")
		except KeyboardInterrupt:
			cmd="exit"

		if cmd=="exit":
			print("Stopping all launched mods...")
			[lists['queue'][i].put(0) for i in running]
			[lists['thread'][i].join() for i in running]
			mod_conf["enabled"]=mod_enabled
			with open(root+"/conf/mods.json") as f:
				json.dump(mod_conf,f,indent=4)
			break

		elif cmd=="help":
			print("N/A")

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
					lists['queue'][mod]=queue.Queue()
					lists['queue'][mod].put(1)
					lists['thread'][mod]=threading.Thread(target=lists['module'][mod].main,args=(mc,lists['queue'][mod])))
					lists['thread'][mod].start()
					running.append(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

		elif re4.match(cmd):
			mod=re4.match(cmd).group().replace("stop ","")
			if mod in mod_list:
				if mod in running:
					lists['queue'][mod].put(0)
					running.remove(mod)
			else:
				print("Invalid mod name: \""+mod+"\"")

	sys.exit()


if __name__=="__main__":
	main()
