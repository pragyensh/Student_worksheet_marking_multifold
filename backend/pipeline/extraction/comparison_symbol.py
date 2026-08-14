from typing import Dict, Any, Tuple
import numpy as np
from .base import BaseExtractor

class ComparisonSymbolExtractor(BaseExtractor):
    """
    Extracts handwritten comparison symbols (<, >, =).
    Uses a tiny 3-class classifier.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initializes the 3-class CNN model.
        """
        self.model_path = model_path
        self.model_loaded = False
        
        if self.model_path:
            # TODO: Load PyTorch/ONNX model weights here
            self.model_loaded = True
            
    def extract(self, image: np.ndarray, region_config: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extracts the symbol from the cropped region.
        """
        if image is None or image.size == 0:
            return "AMBIGUOUS", "low"
            
        if not self.model_loaded:
            # FLAG: Training data insufficient / model weights missing
            return "MISSING_MODEL", "low"
            
        # TODO: Implement actual inference
        # 1. Image preprocessing (grayscale, resize to e.g. 28x28)
        # 2. Model forward pass
        # 3. Map argmax to classes: ['<', '>', '=']
        
        predicted_symbol = "="
        confidence = "medium"
        
        return predicted_symbol, confidence
