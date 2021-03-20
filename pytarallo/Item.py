from typing import Optional, Dict, Any, List
from .Product import Product


class Item:
    """This class implements a pseudo-O(R)M"""
    code: Optional[str]
    features: Dict[str, Any]
    product: Product
    contents: List[Any]  # Other Item objects, actually
    location: List[Any]

    def __init__(self, data: dict = None):
        """
        Items are created by the get_item method
        params: data: a dict() containing the item's data.
        """
        self.code = None
        self.features = {}
        self.product = None
        # http://localhost:8080/v2/items/R777?separate
        self.contents = list()
        self.location = list()

        if data is not None:
            # setup path and location
            # location: the most specific position where the item is located, e.g. "Table"
            # path: a list representing the hierarchy of locations the item, e.g. ["Polito", "Chernobyl", "Table"]
            # the tarallo server returns an JSON object containing only the "location" attribute, which corresponds
            # to the path as defined above
            if data.get('code') is not None:
                self.code = data['code']

            if data.get('product') is not None:
                self.product = Product(data['product'])

            for k, v in data['features'].items():
                # setattr(self, k, v)
                self.features[k] = v

            if data.get('location') is not None:
                self.location = data['location']

            # load the eventual list of items (content) of the item from data
            if data.get('contents') is not None:
                self.set_contents(data.get('contents'))

    def set_contents(self, contents: list = None):
        """setter for the contents of the object"""
        for inner_item_data in contents:
            self.contents.append(Item(inner_item_data))

    def serializable(self):
        result = {}
        if self.code is not None:
            result['code'] = self.code

        if self.location is not None:
            result['location'] = self.location

        result['features'] = self.features
        if len(self.contents) > 0:
            result['contents'] = []
            for item in self.contents:
                # Yay for recursion!
                result['contents'].append(item.serializable())
        return result

    def add_feature(self, key: str, value: Any):
        self.features[key] = value

    def add_content(self, item: Any):
        self.contents.append(Item(item))

    def set_location(self, location: list):
        self.location = location



    def __str__(self):
        s = str(self.features)
        for e in self.contents:
            s = s + "\n"
            s = s + str(e)
        return s
