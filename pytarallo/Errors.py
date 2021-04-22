from requests.exceptions import ConnectionError


class ItemNotFoundError(Exception):
    def __init__(self, code):
        self.code = code


class ProductNotFoundError(Exception):
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


class InvalidObjectError(Exception):
    """
    Object can be an Item, a Product, or other.
    """
    pass


class NoInternetConnectionError(Exception):
    """
    Your computer is not connected to the Internet, hence it can't connect to the T.A.R.A.L.L.O.
    """
    pass


# custom Python decorator
def raises_no_internet_connection_error(func):
    def inner(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except ConnectionError:
            raise NoInternetConnectionError("Your computer is not connected to the Internet.")
    return inner
