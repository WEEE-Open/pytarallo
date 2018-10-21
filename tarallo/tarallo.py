"""
Python T.A.R.A.L.L.O. API
"""
import os
import json
import requests

cfg_path = os.path.dirname(__file__)+"/config.json"

class Tarallo(object):

    def __init__(self, cfg=cfg_path):
        try: 
            config_file = open(cfg, "r")
        except FileNotFoundError:
            print("TARALLO: error: Could not open the config file.")
            exit(1) 
        config = json.load(config_file)
        try:
            self.url = config['url']
            self.user = config['user']
            self.passwd = config['passwd']
            self.cookie = None
        except KeyError as e:
            print("TARALLO: error: '%s' value not set." % e.args[0])
            exit(2)

    def login(self):
        """Login on TARALLO"""
        # TODO: To be implemented
        pass
    
    def logout(self):
        """Logout from TARALLO"""
        # TODO: To be implemented
        pass

