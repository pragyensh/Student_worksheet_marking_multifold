from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any, Tuple

class BaseExtractor(ABC):
    """
    Abstract base class for all extraction modules.
    Every extraction module MUST return exactly what is visibly present
    in the image, without ever referencing the answer key.
    """
    
    @abstractmethod
    def extract(self, image: np.ndarray, region_config: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extracts the student response from a cropped region image.
        
        Args:
            image: Cropped numpy array image of the response region.
            region_config: Dictionary containing region metadata (e.g., number of options).
            
        Returns:
            A tuple of (student_response, confidence):
                - student_response: The extracted value as a string (e.g., "A", "60", "BLANK").
                - confidence: "high", "medium", or "low" based purely on visual clarity.
        """
        pass
