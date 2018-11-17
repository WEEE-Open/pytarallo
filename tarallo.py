import json
import requests

VALID_RESPONSES = [200, 204, 400, 403, 404]


class Tarallo(object):
    """This class handles the Tarallo session"""
    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self.session = requests.Session()
        self.response = None

    def _do_request(self, request_function, *args, **kwargs):
        if 'once' in kwargs:
            once = kwargs['once']
            del kwargs['once']
        else:
            once = False

        self.response = request_function(*args, **kwargs)
        if self.response.status_code == 401:
            if once:
                raise SessionError
            if not self.login():
                raise SessionError
            else:
                self.response = request_function(*args, **kwargs)
                if self.response.status_code not in VALID_RESPONSES:
                    raise ServerError

    def _do_request_with_body(self, request_function, *args, **kwargs):
        if 'headers' not in kwargs or kwargs.get('headers') is None:
            kwargs['headers'] = {}
        if "Content-Type" not in kwargs['headers']:
            kwargs['headers']["Content-Type"] = "application/json"
        self._do_request(request_function, *args, **kwargs)

    # requests.Session() wrapper methods
    # These guys implement further checks and a re-login attempt
    # in case of bad response codes.
    def get(self, url):
        self._do_request(self.session.get, url)

    def delete(self, url):
        self._do_request(self.session.delete, url)

    def post(self, url, data, headers=None, once=False):
        self._do_request_with_body(self.session.post, url, data=data, headers=headers, once=once)

    def put(self, url, data, headers=None):
        self._do_request_with_body(self.session.put, url, data=data, headers=headers)

    def patch(self, url, data, headers=None):
        self._do_request_with_body(self.session.patch, url, data=data, headers=headers)

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
        self.post(self.url + '/v1/session', json.dumps(body), once=True)
        if self.response.status_code == 204:
            return True
        else:
            return False

    def status(self):
        """Returns the status_code of v1/session, useful for testing purposes"""
        return self.session.get(self.url + '/v1/session').status_code

    def get_item(self, code):
        """This method returns an Item instance"""
        self.get(self.url + '/v1/items/' + code)
        if self.response.status_code == 200:
            item = Item(json.loads(self.response.content)["data"])
            return item
        elif self.response.status_code == 404:
            raise ItemNotFoundError("Item " + str(code) + " doesn't exist")

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

    def remove_item(self, code):
        """
        Remove an item from the database

        :return: True if successful deletion
                 False if deletion failed
        """
        self.delete(self.url + '/v1/items/' + code)
        self.get(self.url + '/v1/items/' + code + '?depth=0')
        if self.response.status_code == 404:
            return True
        else:
            return False

    def logout(self):
        """
        Logout from TARALLO

        :return:
            True if successful logout
            False if logout failed
        """
        if self.response is None:
            return False
        self.delete(self.url + '/v1/session')
        if self.response.status_code == 204:
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


class ItemNotFoundError(Exception):
    def __init__(self, code):
        self.code = code


class LocationNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class SessionError(Exception):
    pass


class ServerError(Exception):
    pass
