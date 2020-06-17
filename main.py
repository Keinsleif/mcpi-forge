#!/usr/bin/python3

import os
import sys
import re
import threading
import queue
from mcpi import minecraft

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

	running=[]

	for m in mod_enabled:
		exec("import mods."+m+".main")
		exec("q"+m+"=queue.Queue()")
		exec("q"+m+".put(1)")
		exec("t"+m+"=threading.Thread(target=mods."+m+".main.main,args=(mc,q"+m+",'"+abs_path+"/mods/"+m+"'))")
		exec("t"+m+".start()")
		running.append(m)


	while True:
		cmd=input("> ")
		if cmd=="exit":
			for i in running:
				exec("q"+i+".put(0)")
			break
		elif cmd=="help":
			print("nd")
		elif cmd=="list":
			print("Installed Mods:")
			for i in mod_list:
				print(i)
		elif cmd=="list-enabled":
			print("Enabled Mods:")
			for i in mod_enabled:
				print(i)
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
				exec("import mods."+mod+".main")
				exec("q"+mod+"=queue.Queue()")
				exec("q"+mod+".put(1)")
				exec("t"+mod+"=threading.Thread(target=mods."+mod+".main.main,args=(mc,q"+mod+",'"+abs_path+"/mods/"+mod+"'))")
				exec("t"+mod+".start()")
				running.append(mod)
		elif re4.match(cmd):
			mod=re4.match(cmd).group().replace("stop ","")
			if mod in running:
				exec("q"+mod+".put(0)")
				running.remove(mod)
	sys.exit()


if __name__=="__main__":
	main()
