import json
import urllib.parse
from typing import Optional

import requests

from .AuditEntry import AuditEntry, AuditChanges
from .Errors import *
from .Item import Item
from .ItemToUpload import ItemToUpload
from .Product import Product
from .ProductToUpload import ProductToUpload


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

    def __prepare_url(self, url: str) -> str:
        return self.url + '/' + url.lstrip('/')

    def __check_response(self):
        if self.response.status_code == 401:
            raise AuthenticationError
        if self.response.status_code >= 500:
            raise ServerError

    # requests.Session() wrapper methods
    # These guys implement further checks
    @raises_no_internet_connection_error
    def get(self, url: str) -> requests.Response:
        url = self.__prepare_url(url)
        headers = {"Authorization": "Token " + self.token}
        # cookies={"XDEBUG_SESSION": "PHPSTORM"}
        self.response = self.__session.get(url, headers=headers)
        self.__check_response()
        return self.response

    @raises_no_internet_connection_error
    def delete(self, url: str) -> requests.Response:
        url = self.__prepare_url(url)
        headers = {"Authorization": "Token " + self.token}
        self.response = self.__session.delete(url, headers=headers)
        self.__check_response()
        return self.response

    @raises_no_internet_connection_error
    def post(self, url: str, data, headers=None) -> requests.Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token " + self.token
        url = self.__prepare_url(url)
        self.response = self.__session.post(url, data=data, headers=headers)
        self.__check_response()
        return self.response

    @raises_no_internet_connection_error
    def put(self, url: str, data, headers=None) -> requests.Response:
        if headers is None:
            headers = {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        headers["Authorization"] = "Token " + self.token
        url = self.__prepare_url(url)
        self.response = self.__session.put(url, data=data, headers=headers)
        self.__check_response()
        return self.response

    @raises_no_internet_connection_error
    def patch(self, url: str, data, headers=None) -> requests.Response:
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
    def urlencode(part: str):
        return urllib.parse.quote(part, safe='')

    def status(self):
        """
        Returns the status_code of /v2/session, useful for testing purposes.
        """
        try:
            return self.get('/v2/session').status_code
        except AuthenticationError:
            return self.response.status_code

    def get_item(self, code: str, depth_limit: Optional[int] = None):
        """
        Return an Item instance received from the server
        """
        url = f'/v2/items/{self.urlencode(code)}?separate'  # try an Item without product
        if depth_limit is not None:
            url += '?depth=' + str(int(depth_limit))
        self.get(url)
        if self.response.status_code == 200:
            item = Item(json.loads(self.response.content))
            return item
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def get_product_list(self, brand: str, model: str):
        """returns an list of Product retrieved from the server
        Args:
            self, brand: str, model: str, variant: str
        Returns:
            list of Products
        """
        url = f'/v2/products/{self.urlencode(brand)}/{self.urlencode(model)}'
        self.get(url)
        if self.response.status_code == 200:
            res = json.loads(self.response.content)
            product_list = []
            for p in res:
                product_list.append(Product(p))
            return product_list
        elif self.response.status_code == 404:
            raise ProductNotFoundError("Product doesn't exists.")

    def get_product(self, brand: str, model: str, variant: str = "default"):
        """Retrieve a product from the server
        Returns a Product

        :param variant:
        :param brand:
        :param model:
        """
        url = f'/v2/products/{self.urlencode(brand)}/{self.urlencode(model)}/{self.urlencode(variant)}'
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
            self.put(f'/v2/items/{self.urlencode(item.code)}', data=json.dumps(item.serializable()))
            added_item_status = self.response.status_code
        else:
            self.post('/v2/items', data=json.dumps(item.serializable()))
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
        bmv = f"{self.urlencode(product.brand)}/{self.urlencode(product.model)}/{self.urlencode(product.variant)}"
        self.put(f'/v2/products/{bmv}',
                 data=json.dumps(product.serializable()))
        added_product_status = self.response.status_code
        if added_product_status == 201:
            return True
        elif added_product_status == 400 or added_product_status == 404:
            raise ValidationError
        elif added_product_status == 403:
            raise NotAuthorizedError

    def update_item_features(self, code: str, features: dict):
        """
        Send updated features to the database (this is the PATCH endpoint)
        """
        self.patch(f'/v2/items/{self.urlencode(code)}/features', json.dumps(features))
        if self.response.status_code == 200 or self.response.status_code == 204:
            return True
        elif self.response.status_code == 400:
            raise ValidationError("Impossible to update feature/s")
        elif self.response.status_code == 404:
            raise ItemNotFoundError(f"Item {code} doesn't exist")

    def update_product_features(self, brand: str, model: str, variant: str, features: dict):
        bmv = f"{self.urlencode(brand)}/{self.urlencode(model)}/{self.urlencode(variant)}"
        url = f"/v2/products/{bmv}/features"
        self.patch(url, json.dumps(features))
        if self.response.status_code == 200 or self.response.status_code == 204:
            return True
        elif self.response.status_code == 400:
            raise ValidationError("Impossible to update feature/s")
        elif self.response.status_code == 404:
            raise ProductNotFoundError(f"Product doesn't exist")

    def move(self, code: str, location: str):
        """
        Move an item to another location
        """
        move_status = self.put(f'v2/items/{self.urlencode(code)}/parent', json.dumps(location)).status_code
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

    def delete_product(self, brand: str, model: str, variant: str):
        """
        send a DELETE request to the server to remove a product
        """
        bmv = f"{self.urlencode(brand)}/{self.urlencode(model)}/{self.urlencode(variant)}"
        delete_status = self.delete(f"v2/products/{bmv}").status_code
        if delete_status == 200 or delete_status == 204:
            # Actually deleted
            return True
        if delete_status == 404:
            return None
        else:
            return False

    def remove_item(self, code: str):
        """
        Remove an item from the database

        :return: True if successful deletion
                 False if deletion failed
        """
        item_status = self.delete(f'/v2/items/{self.urlencode(code)}').status_code
        deleted_status = self.get(f'/v2/deleted/{self.urlencode(code)}').status_code
        if deleted_status == 200:
            # Actually deleted
            return True
        if item_status == 404 and deleted_status == 404:
            # ...didn't even exist in the first place? Well, ok...
            return None  # Tri-state FTW!
        else:
            return False

    def restore_item(self, code: str, location: str):
        """
        Restores a deleted item

        :return: True if item successfully restored
                 False if failed to restore
        """
        item_status = self.put(f'/v2/deleted/{self.urlencode(code)}/parent', json.dumps(location)).status_code
        if item_status == 201:
            return True
        else:
            return False

    def bulk_add(self, upload, identifier: Optional[str] = None, overwrite: bool = False):
        """
        Perform a bulk add, to import items from peracotta

        :param upload: The parsed json
        :param identifier: Optional text to identify the computer
        :param overwrite: Overwrite if there's a computer with the same identifier
        :return:
        """
        url = '/v2/bulk/add'
        if identifier:
            url += '/' + self.urlencode(identifier)
        if overwrite:
            url += '?overwrite=true'
        result = self.post(url, json.dumps(upload)).status_code
        # 409 if is a duplicate
        if result == 204:
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

    def get_history(self, code: str, limit: Optional[int] = None):
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
