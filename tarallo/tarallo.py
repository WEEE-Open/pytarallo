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
        self.request = None
        self.cookie = None
 
    def login(self):
        """Login on TARALLO"""
        # TODO: To be implemented (copy from the goddamn bot)
        pass
    
    def logout(self):
        """Logout from TARALLO"""
        # TODO: To be implemented (same as login)
        pass

