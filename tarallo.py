import json
import urllib.parse
import requests

VALID_RESPONSES = [200, 204, 400, 403, 404]


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

        final_url = self.url
        for piece in url_components:
            final_url = urllib.parse.urljoin(final_url, piece)

        args = tuple([final_url]) + args[1:]

        self.response = request_function(*args, **kwargs)
        if self.response.status_code == 401:
            if once:
                raise SessionError
            if not self.login():
                raise SessionError
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
    def get(self, url, once=False):
        self._do_request(self._session.get, url, once=once)
        return self.response

    def delete(self, url):
        self._do_request(self._session.delete, url)
        return self.response

    def post(self, url, data, headers=None, once=False):
        self._do_request_with_body(self._session.post, url, data=data, headers=headers, once=once)
        return self.response

    def put(self, url, data, headers=None):
        self._do_request_with_body(self._session.put, url, data=data, headers=headers)
        return self.response

    def patch(self, url, data, headers=None):
        self._do_request_with_body(self._session.patch, url, data=data, headers=headers)
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
        except SessionError:
            return self.response.status_code

    def get_item(self, code):
        """This method returns an Item instance"""
        self.get(['/v1/items/', self.urlencode(code)])
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
        self.delete(['/v1/items/', self.urlencode(code)])
        self.get(['/v1/items/', self.urlencode(code), '?depth=0'])
        if self.response.status_code == 404:
            return True
        else:
            return False
    
    def restore_item(self, code):
        """
        Restore a deleted item

        :return: True if item successfully restored
                 False if failed to restore
        """
        # TODO: To be implemented
        pass

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
    def __init__(self, data):
        """
        Items are generally created by the get_item method
        But could be created somewhere else and then added to the
        database using the add_item method
        params: data: a dict() containing the item's data.
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
