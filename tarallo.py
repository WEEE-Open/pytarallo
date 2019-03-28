import json
import urllib.parse
from typing import Optional, Dict, Any, List

import requests

VALID_RESPONSES = [200, 201, 204, 400, 403, 404]


class Tarallo(object):
    """This class handles the Tarallo session"""

    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self._session = requests.Session()
        self.response = None

    def _do_request(self, request_function, *args, **kwargs):
        if 'once' in kwargs:
            once = kwargs['once']
            del kwargs['once']
        else:
            once = False

        # Turn it into a list of pieces
        if isinstance(args[0], str):
            url_components = [args[0]]
        else:
            url_components = args[0]

        # Best library to join url components: this thing.
        final_url = '/'.join(s.strip('/') for s in [self.url] + url_components)

        args = tuple([final_url]) + args[1:]

        self.response = request_function(*args, **kwargs)
        if self.response.status_code == 401:
            if once:
                raise AuthenticationError
            if not self.login():
                raise AuthenticationError
            # Retry, discarding previous response
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
    def get(self, url, once=False) -> requests.Response:
        self._do_request(self._session.get, url, once=once)
        return self.response

    def delete(self, url) -> requests.Response:
        self._do_request(self._session.delete, url)
        return self.response

    def post(self, url, data, headers=None, once=False) -> requests.Response:
        self._do_request_with_body(self._session.post, url, data=data, headers=headers, once=once)
        return self.response

    def put(self, url, data, headers=None) -> requests.Response:
        self._do_request_with_body(
            self._session.put, url, data=data, headers=headers)
        return self.response

    def patch(self, url, data, headers=None) -> requests.Response:
        # , cookies={"XDEBUG_SESSION": "PHPSTORM"}
        self._do_request_with_body(
            self._session.patch, url, data=data, headers=headers)
        return self.response

    @staticmethod
    def urlencode(part):
        return urllib.parse.quote(part, safe='')

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
        self.post('/v1/session', json.dumps(body), once=True)
        if self.response.status_code == 204:
            return True
        else:
            return False

    def status(self, retry=True):
        """
        Returns the status_code of v1/session, useful for testing purposes.
        :param retry: Try again if status is "not logged in"

        """
        try:
            return self.get('/v1/session', once=not retry).status_code
        except AuthenticationError:
            return self.response.status_code

    def get_item(self, code, depth_limit=None):
        """This method returns an Item instance"""
        self.get(['/v1/items/', self.urlencode(code)])
        if self.response.status_code == 200:
            item = Item(json.loads(self.response.content)["data"])
            return item
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def add_item(self, item):
        """Add an item to the database"""
        if item.code is not None:  # check whether an item's code was manually added
            self.put([f'/v1/items/{item.code}'],
                     data=json.dumps(item.serializable()))
            added_item_status = self.response.status_code
        else:
            self.post(['/v1/items/'], data=json.dumps(item.serializable()))
            added_item_status = self.response.status_code

        if added_item_status == 201:
            item.code = json.loads(self.response.content)["data"]
            item.path = None
            return True
        elif added_item_status == 400 or added_item_status == 404:
            raise ValidationError
        elif added_item_status == 403:
            raise NotAuthorizedError

    def update_features(self, code: str, features: dict):
        """
        Send updated features to the database (this is the PATCH endpoint)
        """
        self.patch(['/v1/items/', self.urlencode(code),
                    '/features'], json.dumps(features))
        if self.response.status_code == 200 or self.response.status_code == 204:
            return True
        elif self.response.status_code == 400:
            raise ValidationError("Impossible to update feature/s")
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def move(self, code, location):
        """
        Move an item to another location
        """
        move_status = self.put(
            ['v1/items/', self.urlencode(code), '/parent'], json.dumps(location)).status_code
        if move_status == 204 or move_status == 201:
            return True
        elif move_status == 400:
            raise ValidationError(f"Cannot move {code} into {location}")
        elif move_status == 404:
            if json.loads(self.response.content)['code'] == 1:
                raise LocationNotFoundError
            else:
                raise ItemNotFoundError(f"Item {code} doesn't exist")
        else:
            raise RuntimeError(f"Move failed with {move_status}")

    def remove_item(self, code):
        """
        Remove an item from the database

        :return: True if successful deletion
                 False if deletion failed
        """
        item_status = self.delete(
            ['/v1/items/', self.urlencode(code)]).status_code
        deleted_status = self.get(
            ['/v1/deleted/', self.urlencode(code)]).status_code
        if deleted_status == 200:
            # Actually deleted
            return True
        if item_status == 404 and deleted_status == 404:
            # ...didn't even exist in the first place? Well, ok...
            return None  # Tri-state FTW!
        else:
            return False

    def restore_item(self, code, location):
        """
        Restores a deleted item

        :return: True if item successfully restored
                 False if failed to restore
        """
        item_status = self.put(
            ['/v1/deleted/', self.urlencode(code), '/parent'], json.dumps(location)).status_code
        if item_status == 201:
            return True
        else:
            return False

    def travaso(self, code, location):
        item = self.get_item(code, 1)
        codes = []
        for inner in item.contents:
            codes.append(inner.get('code'))
        for inner_code in codes:
            self.move(inner_code, location)
        return True

    def logout(self):
        """
        Logout from TARALLO

        :return:
            True if successful logout
            False if logout failed
        """
        if self.response is None:
            return False
        self.delete('/v1/session')
        if self.response.status_code == 204:
            return True
        else:
            return False


class Item(object):
    """This class implements a pseudo-O(R)M"""
    code: Optional[str]
    features: Dict[str, Any]
    contents: List[Any]  # Other Item objects, actually
    location: Optional[str]
    path: List[str]

    def __init__(self, data=None):
        """
        Items are generally created by the get_item method
        But could be created somewhere else and then added to the
        database using the add_item method
        params: data: a dict() containing the item's data.
        """
        self.code = None
        self.features = {}
        self.contents = list()
        self.location = None
        self.path = []

        if data is not None:
            for k, v in data.items():
                setattr(self, k, v)
            self.path = self.location
            if len(self.path) >= 1:
                self.location = self.path[-1:][0]
            else:
                self.location = None

    def serializable(self):
        result = {}
        if self.code is not None:
            result['code'] = self.code
        if self.location is not None:
            result['parent'] = self.location
        result['features'] = self.features
        if len(self.contents) > 0:
            result['contents'] = []
            for item in self.contents:
                # Yay for recursion!
                result['contents'].append(item.serializable())
        return result


class ItemNotFoundError(Exception):
    def __init__(self, code):
        self.code = code


class LocationNotFoundError(Exception):
    """
    When a location where you want to place something... doesn't exists

    E.g. in a move operation, when creating a new item, etc...
    """
    pass


class NotAuthorizedError(Exception):
    """
    When you authenticated successfully, but you're still not authorized to perform some operation

    E.g. creating new users if you aren't an admin, modifying stuff with a read-only account, etc...
    """
    pass


class AuthenticationError(Exception):
    """
    When you authentication (login attempt) fails.

    E.g. wrong password, nonexistent account, account disabled, etc...
    """
    pass


class ValidationError(Exception):
    """
    When the server thinks your actions don't make any sense in real life and rejects them.

    E.g. placing a RAM into a CPU, making a computer a "root item" (only locations can be),
    placing items with mismatched sockets or connectors into each other, etc...
    """
    pass


class ServerError(Exception):
    """
    When the server returns a 500 status.
    """
    pass
