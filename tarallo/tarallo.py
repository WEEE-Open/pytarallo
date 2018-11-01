"""
Python T.A.R.A.L.L.O. API
"""
import os
import requests

class Tarallo(object):

    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self.cookie = None
 
    def login(self):
        """Login on TARALLO"""
        # TODO: To be implemented
        pass
    
    def logout(self):
        """Logout from TARALLO"""
        # TODO: To be implemented
        pass

