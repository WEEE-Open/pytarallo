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
        self.session = None
        self.request = None  # Last request

    def status(self):
        """
        Check the session status
        
        :return:
            True if session is valid
            False if session has expired or user is not authenticated
        """
        if self.session is not None:
            self.request = self.session.get(self.url + '/v1/session')
            if self.request.status_code == 200:
                return True 
            else:
                return False
        else:
            return False

    def login(self):
        """
        Login on Tarallo
        
        :return:
            True if successful login
            False if authentication failed
        """
        body = dict()
        body['username'] = self.user
        body['password'] = self.passwd
        headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.request = self.session.post(self.url + '/v1/session', data=json.dumps(body), headers=headers)

        if self.request.status_code == 204:
            return True
        else:
            self.session = None
            return False

    def get_item(self, code):
        """This method returns an Item instance"""
        self.request = self.session.get(
            self.url + '/v1/items/' + code)

        if self.request.status_code == 200:
            item = Item(json.loads(self.request.content)["data"])
            return item
        elif self.request.status_code == 404:
            raise ValueError("404 - Request succeeded but item doesn't exist")
        else:
            raise ValueError(self.request)

    def add_item(self, item):
        # TODO: To be implemented
        pass

    def logout(self):
        """
        Logout from TARALLO
        
        :return:
            True if successful logout
            False if logout failed 
        """
        if not self.session:
            return False

        self.request = self.session.delete(self.url + '/v1/session')
        if self.request.status_code == 204:
            self.session = None
            return True
        else:
            return False


class Item(object):
    """This class implements an ORM"""

    def __init__(self, data):
        """
        Items are generally created by the get_item method
        But could be created somewhere else and then added to the
        database using the add_item method
        params: data: a dict() containing the json gathered from tarallo
        """
        for k, v in data.items():
            setattr(self, k, v)

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

