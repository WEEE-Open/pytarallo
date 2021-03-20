from typing import Any

from .Product import Product


class ProductToUpload(Product):
    def __init__(self, data: dict):
        super().__init__(data)

        if not self.variant:
            self.variant = 'default'

    def serializable(self) -> dict:
        # Brand, model, variant are part of the URL
        result = {
            'features': self.features,
        }
        return result
