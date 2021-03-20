from typing import Optional, Any

from .Errors import InvalidObjectError
from .Item import Item
from .ItemBase import ItemBase


class ItemToUpload(ItemBase):
    """
    Item not existing on the server
    """
    parent: Optional[str]

    def __init__(self, item: Optional[Item] = None):
        super().__init__()

        if item:
            if not isinstance(item, Item):
                raise TypeError("ItemToUpload takes an Item to clone, or None if you want to build a new item")
            self.code = item.code
            self.features = item.features
            for inner_item_data in item.contents:
                self.add_content(ItemToUpload(inner_item_data))
            if len(item.location) > 0:
                self.parent = item.location[-1]

    def add_content(self, item):
        if not isinstance(item, ItemToUpload):
            raise InvalidObjectError("ItemToUpload can only contain another ItemToUpload")
        self.contents.append(item)

    def set_parent(self, parent: Optional[str]):
        self.parent = parent

    def serializable(self) -> dict:
        result = super().serializable()
        if self.parent is not None:
            result['parent'] = self.parent
        return result

    def set_code(self, code: Optional[str]):
        self.code = code
