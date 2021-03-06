

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
