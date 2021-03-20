from .Item import Item
from typing import Optional, Any


class ItemToUpload(Item):
    """Item not existing on the server"""
    parent: Optional[str]

    def __init__(self, data: dict = None):
        """Constructor for ItemToUpload"""
        super().__init__(data)

        if data.get("parent") is not None:
            # TODO: parent = location[-1]
            self.parent = data["parent"]

    def set_contents(self, contents: dict = None):
        """setter for the contents"""
        for inner_item_data in contents:
            self.contents.append(ItemToUpload(inner_item_data))


    def serializable(self):
        result = {}
        if self.parent is not None:
            result['parent'] = self.parent

        result['features'] = self.features
        if len(self.contents) > 0:
            result['contents'] = []
            for item in self.contents:
                # Yay for recursion!
                result['contents'].append(item.serializable())
        return result

    def add_content(self, item: Any):
        self.contents.append(ItemToUpload(item))
