from typing import Optional, Dict, Any, List
from pytarallo.Product import Product


class Item:
    """This class implements a pseudo-O(R)M"""
    code: Optional[str]
    features: Dict[str, Any]
    product: Product
    contents: List[Any]  # Other Item objects, actually
    location: List[Any]  # TODO: is it a path (place1/place2/place3) or just a string?
    path: List[str]

    def __init__(self, data: dict = None):
        """
        Items are created by the get_item method
        params: data: a dict() containing the item's data.
        """
        self.code = None
        self.features = {}
        self.product = None #TODO: can't find a reference on the wiki
        self.contents = list()
        self.location = None
        self.path = [] #TODO: merge with location

        if data is not None:
            # setup path and location
            # location: the most specific position where the item is located, e.g. "Table"
            # path: a list representing the hierarchy of locations the item, e.g. ["Polito", "Chernobyl", "Table"]
            # the tarallo server returns an JSON object containing only the "location" attribute, which corresponds
            # to the path as defined above
            if data.get('code') is not None:
                self.code = data['code']

            for k, v in data['features'].items():
                # setattr(self, k, v)
                self.features[k] = v

            self.path = data.get('location') #TODO: remove, no location in the JSON wiki
            if self.path is not None and len(self.path) >= 1:
                self.location = self.path[-1]

            # load the eventual content of the item from data
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
            result['parent'] = self.location

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

    def set_location(self, location: str):
        self.location = location

    def __str__(self):
        s = str(self.features)
        for e in self.contents:
            s = s + "\n"
            s = s + str(e)
        return s
