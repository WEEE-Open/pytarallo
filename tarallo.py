import json
import requests


class Tarallo(object):
    """This class handles the Tarallo session"""
    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self.session = requests.Session()
        self.last_request = None

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
        self.last_request = self.session.post(self.url + '/v1/session', data=json.dumps(body), headers=headers)

        if self.last_request.status_code == 204:
            return True
        else:
            return False

    def status(self):
        """Returns the status_code of v1/session, useful for testing purposes"""
        return self.session.get(self.url + '/v1/session').status_code

    def retry_login(self):
        """This method retries to login if the session has expired"""
        if not self.login():
            raise SessionError

    def get_item(self, code):
        """This method returns an Item instance"""
        self.last_request = self.session.get(self.url + '/v1/items/' + code)
        if self.last_request.status_code == 200:
            item = Item(json.loads(self.last_request.content)["data"])
            return item
        elif self.last_request.status_code == 404:
            raise ItemNotFoundException("404 - Request succeeded but item "+str(code)+ " doesn't exist")
        else:
            self.retry_login()
            return self.get_item(code)

    def add_item(self, item):
        """Add an item to the database"""
        # TODO: To be implemented
        pass

    def commit(self, item):
        """Commit an updated Item to the database"""
        # TODO: To be implemented
        pass

    def move(self, item, location):
        """
        Move an item to another location
        """
        # TODO: To be implemented
        pass

    def remove_item(self, item):
        """Remove an item from the database"""
        # TODO: To be implemented
        pass

    def logout(self):
        """
        Logout from TARALLO

        :return:
            True if successful logout
            False if logout failed
        """
        if self.last_request is None:
            return False
        self.last_request = self.session.delete(self.url + '/v1/session')
        if self.last_request.status_code == 204:
            return True
        else:
            return False


class Item(object):
    """This class implements a pseudo-O(R)M"""
    def __init__(self, data):
        """
        Items are generally created by the get_item method
        But could be created somewhere else and then added to the
        database using the add_item method
        params: data: a dict() containing the json gathered from tarallo
        """
        for k, v in data.items():
            setattr(self, k, v)


class ItemNotFoundException(Exception):
    def __init__(self,code):
        self.code=code


class LocationNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class SessionError(Exception):
    pass
