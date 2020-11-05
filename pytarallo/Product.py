from typing import Optional, Dict, Any


class Product:
    """Not sure of what this should represent"""
    brand: Optional[str]
    model: Optional[str]
    variant: Optional[str]
    features: Dict[str, Any]

    def __init__(self, data: dict = None):
        """Constructor for Product"""
        self.brand = None
        self.model = None
        self.variant = None
        self.features = {}

        if data is not None:
            self.brand = data['brand']
            self.model = data['model']
            self.variant = data['variant']
            self.features = data['features']

    def serializable(self):
        """JSON representation

        Args:
            self

        Returns:
            a dict for the JSON repr

        """
        result = {}
        if self.brand is not None:
            result['brand'] = self.brand
        elif self.model is not None:
            result['model'] = self.model
        elif self.variant is not None:
            result['variant'] = self.variant
        elif self.features is not None:
            result['features'] = self.features

        return result

    def add_feature(self, key: str, value: Any):
        self.features[key] = value
