import cv2
import numpy as np
from typing import Dict, Tuple, Any

class RegionCropper:
    def __init__(self, region_definitions: Dict[str, Dict[str, Any]]):
        """
        Initializes the cropper with region definitions.
        region_definitions format:
        {
            "q1": {"type": "mcq", "bbox": [x1, y1, x2, y2]},
            ...
        }
        """
        self.regions = region_definitions
        
    def crop_regions(self, aligned_image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Crops all defined regions from the aligned image.
        Returns a dictionary mapping region_id to the cropped image (numpy array).
        """
        crops = {}
        for region_id, definition in self.regions.items():
            if "bbox" not in definition:
                continue
            
            x1, y1, x2, y2 = definition["bbox"]
            
            # Ensure coordinates are within image bounds
            h, w = aligned_image.shape[:2]
            x1 = max(0, min(x1, w))
            y1 = max(0, min(y1, h))
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
            
            # Crop
            if y2 > y1 and x2 > x1:
                crop = aligned_image[y1:y2, x1:x2].copy()
                crops[region_id] = crop
            else:
                # Invalid bounding box
                crops[region_id] = None
                
        return crops
