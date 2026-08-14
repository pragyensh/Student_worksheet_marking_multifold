import cv2
import numpy as np
from typing import Optional

class PageDetector:
    def __init__(self):
        pass

    def detect_page(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detects the largest rectangular contour in the image, assumed to be the worksheet.
        Returns the 4 corner points of the document, or None if not found.
        """
        # Convert to grayscale and blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edged = cv2.Canny(blurred, 75, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        document_contour = None
        
        # Loop over contours to find a 4-point polygon
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                document_contour = approx
                break
                
        if document_contour is not None:
            return document_contour.reshape(4, 2)
            
        # Fallback to image corners if no document contour found
        h, w = image.shape[:2]
        return np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype="float32")
