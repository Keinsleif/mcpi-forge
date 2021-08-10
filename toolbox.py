#!/usr/bin/python3

import os, sys, json

class ConfigManager(object):
    def __init__(self,root):
        self.config_path = os.path.join(root,"conf")
        self.main_conf = os.path.join(self.config_path,"main.json")
        self.mod_conf_path = os.path.join(self.config_path,"mods")

    def load_config(self):
        mod_confs = []
        for i in os.listdir(self.mod_conf_path):
            if os.path.splitext(i)[1] == ".json":
                mods_conf.append(i)