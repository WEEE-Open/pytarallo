"""
Python T.A.R.A.L.L.O. API
"""
import os
import json
import requests


class Tarallo(object):
    """This class handles the Tarallo session"""
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

    @classmethod
    def get_item(self):
        """This method should return an Item instance"""
        # TODO: To be implemented
        item = Item()
        return item

    def add_item(self, item):
        # TODO: To be implemented
        pass
    
    def logout(self):
        """Logout from TARALLO"""
        # TODO: To be implemented (same as login)
        pass


class Item(object):
    """This class implements an ORM"""
    def __init__(self):
        """Items are generally created by the get_item classmethod
        But could be created somewhere else and then added to the
        database using the add_item method"""
        # TODO: To be implemented
        pass

    def move_to(self, position):
        """Move an item to another position"""
        # TODO: To be implemented
        pass

