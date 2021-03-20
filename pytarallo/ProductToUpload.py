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
        # Brand, model, variant are part of the URL
        result = {
            'features': self.features,
        }
        return result
