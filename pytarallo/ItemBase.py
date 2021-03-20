from typing import Optional, Dict, Any, List


class ItemBase:
    """
    Base class, do not use directly, use Item or ItemToUpload instead
    """
    code: Optional[str]
    features: Dict[str, Any]
    contents: List[Any]

    def __init__(self):
        """
        Items are created by the get_item method
        params: data: a dict() containing the item's data.
        """
        self.code = None
        self.features = {}
        self.contents = list()

    def serializable(self) -> dict:
        result = {}
        if self.code is not None:
            result['code'] = self.code

        result['features'] = self.features

        if len(self.contents) > 0:
            result['contents'] = []
            for item in self.contents:
                # Yay for recursion!
                result['contents'].append(item.serializable())
        return result
