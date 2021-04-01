from typing import Optional, List

from .Errors import InvalidObjectError
from .ItemBase import ItemBase
from .Product import Product


class Item(ItemBase):
    code: str
    location: List[str]
    product: Optional[Product]

    def __init__(self, data: dict, top_level: bool = True):
        """
        Items are created by the get_item method
        params: data: a dict() containing the item's data.

        :top_level: Used for recursion, set to True when calling from outside
        """
        super().__init__()

        # setup path and location
        # location: the most specific position where the item is located, e.g. "Table"
        # path: a list representing the hierarchy of locations the item, e.g. ["Polito", "Chernobyl", "Table"]
        # the tarallo server returns an JSON object containing only the "location" attribute, which corresponds
        # to the path as defined above
        if data.get('code') and len(data.get('code')) > 0:
            self.code = data['code']
        else:
            raise InvalidObjectError("Received item without code")

        if data.get('product'):
            self.product = Product(data['product'])
        else:
            self.product = None

        for k, v in data['features'].items():
            # setattr(self, k, v)
            self.features[k] = v

        if data.get('location'):
            self.location = data['location']
        else:
            if top_level:
                raise InvalidObjectError("Location is missing, not even empty")

        # load the optional list of items (content) of the item from data
        if data.get('contents'):
            for inner_item_data in data.get('contents'):
                self.add_content(Item(inner_item_data, False))

    def add_content(self, item):
        """
        setter for the contents of the item
        """
        if not isinstance(item, Item):
            raise InvalidObjectError("Item can only contain another Item")
        self.contents.append(item)

    def serializable(self) -> dict:
        result = super().serializable()
        result['location'] = self.location
        if self.product:
            result['product'] = self.product.serializable()
        return result

    def __str__(self):
        s = str(self.features)
        for e in self.contents:
            s = s + "\n"
            s = s + str(e)
        return s
