"""
Python T.A.R.A.L.L.O. API
"""
import os
import json
import requests

"""
This variable contains the Tarallo() instance for the working session.
This is meant to be imported in the final script and allocated in there.
"""
tsession = None


class Tarallo(object):
    """This class handles the Tarallo session"""
    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self.request = None  # Last request headers
        self.cookie = None

    def login(self):
        """Login on TARALLO"""
        # TODO: To be implemented (copy from the goddamn bot)
        pass

    @staticmethod
    def get_item(code):
        """This method should return an Item instance"""
        # TODO: To be implemented
        # Grab stuff from tarallo and get the JSON
        # item = Item(insert a dict() here)
        # return item
        pass

    def add_item(self, item):
        # TODO: To be implemented
        pass
    
    def logout(self):
        """Logout from TARALLO"""
        # TODO: To be implemented (same as login)
        pass


class Item(object):
    """This class implements an ORM"""
    def __init__(self, data):
        """
        Items are generally created by the get_item staticmethod
        But could be created somewhere else and then added to the
        database using the add_item method
        params: data: a dict() containing the json gathered from tarallo
        """
        # TODO: To be implemented
        pass

    def move_to(self, position):
        """
        Move an item to another position
        Grab needed stuff from the tsession variable
        and use the tsession for pushing edits
        """
        # TODO: To be implemented
        pass
 

def get_tsession():
    print(tsession)
    return tsession

