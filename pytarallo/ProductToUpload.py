from typing import Any

from .Product import Product


class ProductToUpload(Product):
    def __init__(self, data: dict):
        super().__init__(data)

        if not self.variant:
            self.variant = 'default'

    # TODO: test
    def add_feature(self, key: str, value: Any):
        self.features[key] = value

    def serializable(self) -> dict:
        """
        JSON representation

        :return: a dict for the JSON repr
        """
        result = {}
        if self.brand:
            result['brand'] = self.brand
        if self.model:
            result['model'] = self.model
        if self.variant:
            result['variant'] = self.variant
        if self.features:
            result['features'] = self.features

        return result
