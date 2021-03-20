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
            if data.get('brand') is not None:
                self.brand = data['brand']
            if data.get('model') is not None:
                self.model = data['model']
            if data.get('variant') is not None:
                self.variant = data['variant']
            if data.get('features') is not None:
                self.features = data['features']
            else:
                self.features = {}

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
        if self.model is not None:
            result['model'] = self.model
        if self.variant is not None:
            result['variant'] = self.variant
        if self.features is not None:
            result['features'] = self.features

        return result

    def add_feature(self, key: str, value: Any):
        self.features[key] = value
