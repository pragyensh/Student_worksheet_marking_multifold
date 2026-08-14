import cv2
import numpy as np
from typing import Dict, Any, Tuple, List
from .base import BaseExtractor

class MCQCheckboxExtractor(BaseExtractor):
    """
    Extracts MCQ checkbox selections using classical Computer Vision.
    No ML models are used. Output space: A/B/C/BLANK/MULTIPLE/STRAY_MARK/AMBIGUOUS.
    """
    
    def __init__(self):
        # Threshold for marking a box as "selected" based on fill ratio
        self.FILL_THRESHOLD = 0.05
        
    def extract(self, image: np.ndarray, region_config: Dict[str, Any]) -> Tuple[str, str]:
        if image is None or image.size == 0:
            return "AMBIGUOUS", "low"
            
        num_options = region_config.get("options", 2)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding to isolate dark ink/pencil marks from white background
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10
        )
        
        # We need to find the printed boxes or at least divide the region.
        # For simplicity in this baseline, if we assume horizontal layout,
        # we can divide the width by num_options.
        # A more robust approach finds the actual square contours.
        
        h, w = thresh.shape
        layout = region_config.get("layout", "horizontal")
        
        selections = []
        
        for i in range(num_options):
            if layout == "horizontal":
                segment_width = w // num_options
                x_start = i * segment_width
                x_end = (i + 1) * segment_width
                segment = thresh[:, x_start:x_end]
                pad_x = int(segment_width * 0.25)
                pad_y = int(h * 0.25)
                roi = segment[pad_y:h-pad_y, pad_x:segment_width-pad_x]
            else:
                segment_height = h // num_options
                y_start = i * segment_height
                y_end = (i + 1) * segment_height
                segment = thresh[y_start:y_end, :]
                pad_x = int(w * 0.25)
                pad_y = int(segment_height * 0.25)
                roi = segment[pad_y:segment_height-pad_y, pad_x:w-pad_x]
            
            # Calculate ratio of dark pixels to total area in ROI
            total_pixels = roi.shape[0] * roi.shape[1]
            if total_pixels == 0:
                continue
                
            dark_pixels = cv2.countNonZero(roi)
            fill_ratio = dark_pixels / total_pixels
            
            if fill_ratio > self.FILL_THRESHOLD:
                # Option selected
                # Map 0 -> A, 1 -> B, 2 -> C, etc.
                selections.append(chr(ord('A') + i))
                
        # Determine final response
        if len(selections) == 1:
            return selections[0], "high"
        elif len(selections) > 1:
            return "MULTIPLE", "high"
        else:
            # Check if there are stray marks outside the expected ROI but inside the crop
            # If the whole region has marks but not in the boxes
            total_dark = cv2.countNonZero(thresh)
            expected_empty_ratio = total_dark / (w * h)
            
            if expected_empty_ratio > 0.02:
                return "STRAY_MARK", "medium"
                
            return "BLANK", "high"
