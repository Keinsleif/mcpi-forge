#!/usr/bin/python3

import os
import sys
import re
import threading
import queue
from mcpi import minecraft
from importlib import import_module

print("Welcome to Minecraft Pi Forge.")
abs_path=os.path.dirname(os.path.abspath(__file__))

def main():
	mod_list=os.listdir(abs_path+"/mods/")
	mod_enabled=os.listdir(abs_path+"/conf/enabled/")
	mc=minecraft.Minecraft.create()
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
		lists['thread'][m]=threading.Thread(target=lists['module'][m].main,args=(mc,lists['queue'][m],abs_path+"/mods/"+m))
		lists['thread'][m].start()
		running.append(m)


	while True:
		cmd=input("> ")
		if cmd=="exit":
			[lists['queue'][i].put(0) for i in running]
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
					with open(abs_path+"/conf/enabled/"+mod,"w") as f:
						f.write(" ")
					mod_enabled.append(mod)
			else:
				print("Mod doesn't exist.")
		elif re2.match(cmd):
			mod=re2.match(cmd).group().replace("disable ","")
			if mod in mod_list:
				if mod in mod_enabled:
					os.remove(abs_path+"/conf/enabled/"+mod)
					mod_enabled.remove(mod)
			else:
				print("Mod doesn't exist.")
		elif re3.match(cmd):
			mod=re3.match(cmd).group().replace("start ","")
			if mod in mod_list:
				lists['module'][mod]=import_module("mods."+mod+".main")
				lists['queue'][mod]=queue.Queue()
				lists['queue'][mod].put(1)
				lists['thread'][mod]=threading.Thread(target=lists['module'][mod].main,args=(mc,lists['queue'][mod],abs_path+"/mods/"+mod)))
				lists['thread'][mod].start()
				running.append(mod)
		elif re4.match(cmd):
			mod=re4.match(cmd).group().replace("stop ","")
			if mod in running:
				lists['queue'][mod].put(0)
				running.remove(mod)
	sys.exit()


if __name__=="__main__":
	main()
