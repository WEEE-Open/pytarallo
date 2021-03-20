import json
import urllib.parse
from typing import Optional

import requests

from .Product import Product
from .ProductToUpload import ProductToUpload
from .Item import Item
from .ItemToUpload import ItemToUpload
from .AuditEntry import AuditEntry, AuditChanges
from .Errors import *

VALID_RESPONSES = [200, 201, 204, 400, 403, 404]


class Tarallo(object):
    """This class handles the Tarallo session"""

    def __init__(self, url: str, token: str):
        """
        :param url: Tarallo URL
        :param token: Token (go to Options > Get token)
        """
        self.url = url.rstrip('/')
        self.token = token.strip()
        self.__session = requests.Session()
        self.response = None

    def __prepare_url(self, url):
        if isinstance(url, str):
            url = '/' + url.lstrip('/')
        else:
            # Best library to join url components: this thing.
            url = '/' + '/'.join(s.strip('/') for s in url)
        return self.url + url

    def __check_response(self):
        if self.response.status_code == 401:
            raise AuthenticationError
        if self.response.status_code not in VALID_RESPONSES:
            raise ServerError

    # requests.Session() wrapper methods
    # These guys implement further checks
    def get(self, url) -> requests.Response:
        url = self.__prepare_url(url)
        headers = {"Authorization": "Token " + self.token}
        # cookies={"XDEBUG_SESSION": "PHPSTORM"}
        self.response = self.__session.get(url, headers=headers)
        self.__check_response()
        return self.response

    def delete(self, url) -> requests.Response:
        url = self.__prepare_url(url)
        headers = {"Authorization": "Token " + self.token}
        self.response = self.__session.delete(url, headers=headers)
        self.__check_response()
        return self.response

    def post(self, url, data, headers=None) -> requests.Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token " + self.token
        url = self.__prepare_url(url)
        self.response = self.__session.post(url, data=data, headers=headers)
        self.__check_response()
        return self.response

    def put(self, url, data, headers=None) -> requests.Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token " + self.token
        url = self.__prepare_url(url)
        self.response = self.__session.put(url, data=data, headers=headers)
        self.__check_response()
        return self.response

    def patch(self, url, data, headers=None) -> requests.Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token " + self.token
        url = self.__prepare_url(url)
        self.response = self.__session.patch(url, data=data, headers=headers)
        self.__check_response()
        return self.response

    @staticmethod
    def urlencode(part):
        return urllib.parse.quote(part, safe='')

    def status(self):
        """
        Returns the status_code of /v2/session, useful for testing purposes.
        """
        try:
            return self.get('/v2/session').status_code
        except AuthenticationError:
            return self.response.status_code

    def get_item(self, code, depth_limit=None):
        """This method returns an Item instance received from the server"""
        url = '/v2/items/' + self.urlencode(code) + '?separate'  # try an Item without product6
        if depth_limit is not None:
            url += '?depth=' + str(int(depth_limit))
        self.get(url)
        if self.response.status_code == 200:
            item = Item(json.loads(self.response.content))
            return item
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def get_product_list(self, brand, model):
        """returns an list of Product retrieved from the server
        Args:
            self, brand: str, model: str, variant: str
        Returns:
            list of Products
        """
        url = '/v2/products/' + brand + '/' + model
        self.get(url)
        if self.response.status_code == 200:
            res = json.loads(self.response.content)
            product_list = []
            for p in res:
                product_list.append(Product(p))
            return product_list
        elif self.response.status_code == 404:
            raise ProductNotFoundError("Product doesn't exists.")

    def get_product(self, brand, model, variant="default"):
        """Retrieve a product from the server
        Returns a Product

        :param variant:
        :param brand:
        :param model:
        """
        url = '/v2/products/' + brand + '/' + model + '/' + variant
        self.get(url)
        if self.response.status_code == 200:
            res = json.loads(self.response.content)
            p = Product(res)
            return p
        elif self.response.status_code == 404:
            raise ProductNotFoundError("Product doesn't exists.")

    def add_item(self, item: ItemToUpload):
        """Add an item to the database and eventually update its code
            """
        if item.code is not None:  # check whether an item's code was manually added
            self.put([f'/v2/items/{item.code}'],
                     data=json.dumps(item.serializable()))
            added_item_status = self.response.status_code
        else:
            self.post(['/v2/items/'], data=json.dumps(item.serializable()))
            added_item_status = self.response.status_code
        if added_item_status == 201:
            item.code = json.loads(self.response.content)
            return True
        elif added_item_status == 400 or added_item_status == 404:
            raise ValidationError
        elif added_item_status == 403:
            raise NotAuthorizedError

    def add_product(self, product: ProductToUpload):
        """adds a product to the database
        Args:
            self, product: ProductToUpload
        Returns:
            True if success, Errors exceptions otherwise
        """
        self.put([f'/v2/products/{product.brand}/{product.model}/{product.variant}'],
                 data=json.dumps(product.serializable()))
        added_product_status = self.response.status_code
        if added_product_status == 201:
            return True
        elif added_product_status == 400 or added_product_status == 404:
            raise ValidationError
        elif added_product_status == 403:
            raise NotAuthorizedError

    def update_item_features(self, code: str, features: dict):
        # TODO: add the update feature for the products, 2 functions?
        """
        Send updated features to the database (this is the PATCH endpoint)
        """
        self.patch(['/v2/items/', self.urlencode(code),
                    '/features'], json.dumps(features))
        if self.response.status_code == 200 or self.response.status_code == 204:
            return True
        elif self.response.status_code == 400:
            raise ValidationError("Impossible to update feature/s")
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def update_product_features(self, brand, model, variant, features: dict):
        # TODO: tests
        url = f"/v2/products/{brand}/{model}/{variant}/features"
        self.patch(url, json.dumps(features))
        if self.response.status_code == 200 or self.response.status_code == 204:
            return True
        elif self.response.status_code == 400:
            raise ValidationError("Impossible to update feature/s")
        elif self.response.status_code == 404:
            raise ProductNotFoundError(f"Product doesn't exist")

    def move(self, code, location):
        """
        Move an item to another location
        """
        move_status = self.put(
            ['v2/items/', self.urlencode(code), '/parent'], json.dumps(location)).status_code
        if move_status == 204 or move_status == 201:
            return True
        elif move_status == 400:
            raise ValidationError(f"Cannot move {code} into {location}")
        elif move_status == 404:
            response_json = json.loads(self.response.content)
            if 'item' not in response_json:
                raise ServerError("Server didn't find an item, but isn't telling us which one")
            if response_json['item'] == location:
                raise LocationNotFoundError
            else:
                raise ItemNotFoundError(f"Item {response_json['item']} doesn't exist")
        else:
            raise RuntimeError(f"Move failed with {move_status}")

    def delete_product(self, brand, model, variant):
        """ send a DELETE request to the server to remove a product
        
        Args:
            self, brand, model, variant
           
        Returns:
            /
        """
        delete_status = self.delete(
            [f"v2/products/{brand}/{model}/{variant}"]
        )
        if delete_status == 200:
            # Actually deleted
            return True
        if delete_status == 404:
            return None
        else:
            return False

    def remove_item(self, code):
        """
        Remove an item from the database

        :return: True if successful deletion
                 False if deletion failed
        """
        item_status = self.delete(['/v2/items/', self.urlencode(code)]).status_code
        deleted_status = self.get(['/v2/deleted/', self.urlencode(code)]).status_code
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
        item_status = self.put(['/v2/deleted/', self.urlencode(code), '/parent'], json.dumps(location)).status_code
        if item_status == 201:
            return True
        else:
            return False

    def travaso(self, code, location):
        item = self.get_item(code, 1)
        codes = []
        for inner_item in item.contents:
            codes.append(inner_item.code)
        for inner_code in codes:
            self.move(inner_code, location)
        return True

    def get_history(self, code, limit: Optional[int] = None):
        url = f'/v2/items/{self.urlencode(code)}/history'
        if limit is not None:
            url += '?length=' + str(int(limit))
        history = self.get(url)

        if history.status_code == 200:
            result = []
            for entry in history.json():
                try:
                    change = AuditChanges(entry["change"])
                except ValueError:
                    change = AuditChanges.Unknown
                result.append(AuditEntry(entry["user"], change, float(entry["time"]), entry["other"]))
            return result
        elif history.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn\'t exist")
        else:
            raise RuntimeError("Unexpected return code")

    def get_codes_by_feature(self, feature: str, value: str):
        url = f"/v2/features/{self.urlencode(feature)}/{self.urlencode(value)}"
        items = self.get(url)

        if items.status_code == 200:
            return items.json()
        elif items.status_code == 400:
            exception = items.json()
            raise ValidationError(exception.get('message', 'No message from the server'))
        else:
            raise RuntimeError("Unexpected return code")
