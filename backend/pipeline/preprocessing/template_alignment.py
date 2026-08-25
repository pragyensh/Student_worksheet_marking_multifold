import cv2
import numpy as np

class TemplateAligner:
    def __init__(self, template_path: str):
        """
        Initializes the aligner with a template image.
        Uses ORB for fast feature matching.
        """
        # Load template image
        try:
            self.template = cv2.imread(template_path)
        except Exception as e:
            print(f"Warning: Could not load template due to {e}")
            self.template = None
            
        if self.template is None:
            print(f"Template load failed for {template_path}, bypassing alignment.")
            self.desc_template = None
            return
            
        # Use ORB instead of SIFT for memory efficiency
        self.orb = cv2.ORB_create(nfeatures=1000)
        
        # Compute keypoints for template
        gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        try:
            self.kp_template, self.desc_template = self.orb.detectAndCompute(gray, None)
        except Exception as e:
            print(f"Warning: Could not compute template features: {e}. Alignment will be bypassed.")
            self.kp_template, self.desc_template = None, None
            
        # Use BFMatcher with HAMMING for ORB
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def align(self, image: np.ndarray) -> np.ndarray:
        """
        Aligns the input image to the template.
        """
        if self.desc_template is None:
            return image
            
        # Find keypoints in target
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kp_image, desc_image = self.orb.detectAndCompute(gray_image, None)
        
        if desc_image is None or len(desc_image) < 10:
            return image
            
        # Match descriptors
        matches = self.matcher.match(self.desc_template, desc_image)
        
        # Sort by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep top matches
        good_matches = matches[:int(len(matches) * 0.15)]
        
        if len(good_matches) < 4:
            return image # Need at least 4 points for homography
            
        # Extract location of good matches
        points_input = np.zeros((len(good_matches), 2), dtype=np.float32)
        points_ref = np.zeros((len(good_matches), 2), dtype=np.float32)
        
        for i, match in enumerate(good_matches):
            points_ref[i, :] = self.kp_template[match.queryIdx].pt
            points_input[i, :] = kp_image[match.trainIdx].pt
            
        # Find homography
        h, mask = cv2.findHomography(points_input, points_ref, cv2.RANSAC, 5.0)
        
        if h is None:
            return image
            
        # Warp image
        height, width = self.template.shape[:2]
        aligned_image = cv2.warpPerspective(image, h, (width, height))
        
        return aligned_image
