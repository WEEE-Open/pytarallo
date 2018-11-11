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
        self.request = None  # Last request
        self.cookie = None

    def status(self):
        """
        Check the session status
        
        :return:
            True if session is valid
            False if session has expired or user is not authenticated
        """
        if self.cookie is not None:
            self.request = requests.get(self.url + '/v1/session', cookies=self.cookie)
            if self.request.status_code == 200:
                return True
            if self.request.status_code != 403:
                return False
        else:
            return False

    def login(self):
        """Login on Tarallo"""
        body = dict()
        body['username'] = self.user
        body['password'] = self.passwd
        headers = {"Content-Type": "application/json"}
        self.request = requests.post(self.url + '/v1/session', data=json.dumps(body), headers=headers)

        if self.request.status_code == 204:
            self.cookie = self.request.cookies
            return True

        else:
            return False

    def get_item(self, code):
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
        headers = {"Content-Type": "application/json"}
        self.request = requests.delete(self.url + '/v1/session', headers=headers, cookies=self.cookie)
        if self.request.status_code == 204:
            self.cookie = None
            return True
        else:
            return False


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

    def move_to(self, location):
        """
        Move an item to another location
        Grab needed stuff from the tsession variable
        and use the tsession for pushing edits
        """
        # TODO: To be implemented
        pass


def get_tsession():
    return tsession
