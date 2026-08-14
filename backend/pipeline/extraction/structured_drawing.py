import cv2
import numpy as np
import json
from typing import Dict, Any, Tuple
from .base import BaseExtractor

class StructuredDrawingExtractor(BaseExtractor):
    """
    Extracts structured data (like tens and ones count) from student drawings.
    Uses connected-component (blob) analysis to distinguish between large bundles (tens)
    and small isolated marks (ones).
    """
    
    def __init__(self):
        # Parameters for separating tens from ones based on blob size
        self.MIN_ON_PIXELS = 10      # Ignore noise smaller than this
        self.TEN_BUNDLE_MIN_AREA = 200 # A ten bundle is large
        
    def extract(self, image: np.ndarray, region_config: Dict[str, Any]) -> Tuple[str, str]:
        if image is None or image.size == 0:
            return "AMBIGUOUS", "low"
            
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptive threshold to isolate ink
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10
        )
        
        # Morphological operations to join broken strokes within a single drawing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)
        
        tens_count = 0
        ones_count = 0
        
        # Start from 1 to ignore the background (label 0)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            
            if area < self.MIN_ON_PIXELS:
                continue # Noise
                
            if area >= self.TEN_BUNDLE_MIN_AREA:
                tens_count += 1
            else:
                ones_count += 1
                
        if tens_count == 0 and ones_count == 0:
            return "BLANK", "high"
            
        result_dict = {
            "tens": tens_count,
            "ones": ones_count
        }
        
        # The scorer will expect a string representation
        return json.dumps(result_dict), "high"
