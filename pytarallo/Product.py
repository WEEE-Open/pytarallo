from typing import Optional, Dict, Any


class Product:
    brand: Optional[str]
    model: Optional[str]
    variant: Optional[str]
    features: Dict[str, Any]

    def __init__(self, data=None):
        """Constructor for Product"""
        if data is None:
            data = {}
        # Defaults to None if anything is missing, this is expected
        self.brand = data.get('brand')
        self.model = data.get('model')
        self.variant = data.get('variant')
        self.features = data.get('features')

    def serializable(self) -> dict:
        result = {
            'brand': self.brand,
            'model': self.model,
            'variant': self.variant,
            'features': self.features,
        }
        return result
