from typing import Optional, Dict, Any, List


class Item:
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
                # setattr(self, k, v)
                self.features[k] = v

            # TODO: what's happening here?
    ''' self.path = self.location
            if len(self.path) >= 1:
                self.location = self.path[-1:][0]
            else:
                self.location = None'''

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
