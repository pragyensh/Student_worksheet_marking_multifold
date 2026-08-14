import cv2
import numpy as np
from typing import Dict, Any, List
import os
import json

from .preprocessing.page_detector import PageDetector
from .preprocessing.perspective import four_point_transform
from .preprocessing.template_alignment import TemplateAligner
from .cropping.cropper import RegionCropper
from .cropping.region_definitions import load_region_definitions
from .scoring.scorer import DeterministicScorer

# Extractors
from .extraction.mcq_checkbox import MCQCheckboxExtractor
from .extraction.handwritten_numeral import HandwrittenNumeralExtractor
from .extraction.comparison_symbol import ComparisonSymbolExtractor
from .extraction.devanagari_text import DevanagariTextExtractor
from .extraction.structured_drawing import StructuredDrawingExtractor
from .extraction.fallback_vlm import FallbackVLMExtractor

class PipelineOrchestrator:
    def __init__(self, template_id: str, templates_dir: str = "backend/templates"):
        self.template_id = template_id
        
        # Load configs
        self.region_defs = load_region_definitions(template_id, templates_dir)
        self.answer_key = self._load_answer_key(template_id, templates_dir)
        
        # Initialize preprocessing
        template_img_path = os.path.join(templates_dir, template_id, "template_image.jpg")
        self.aligner = TemplateAligner(template_img_path)
        self.page_detector = PageDetector()
        self.cropper = RegionCropper(self.region_defs["regions"])
        
        # Initialize extractors
        self.extractors = {
            "mcq": MCQCheckboxExtractor(),
            "numeral": HandwrittenNumeralExtractor(),
            "symbol": ComparisonSymbolExtractor(),
            "devanagari": DevanagariTextExtractor(),
            "structured_drawing": StructuredDrawingExtractor(),
            "fallback": FallbackVLMExtractor()
        }
        
        # Initialize scorer
        self.scorer = DeterministicScorer()
        
    def _load_answer_key(self, template_id: str, templates_dir: str) -> Dict[str, Any]:
        path = os.path.join(templates_dir, template_id, "answer_key.json")
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # convert list to dict mapping region_id -> entry
            return {entry["region_id"]: entry for entry in data.get("regions", [])}
            
    def process_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs the full pipeline on a raw photo of a worksheet.
        """
        results = []
        
        # Stage 1: Page detection and perspective correction
        pts = self.page_detector.detect_page(image)
        if pts is not None:
            flat_image = four_point_transform(image, pts)
        else:
            flat_image = image
            
        # Stage 2: Template alignment
        aligned_image = self.aligner.align(flat_image)
        
        # Stage 3: Region cropping
        crops = self.cropper.crop_regions(aligned_image)
        
        # Stage 4 & 5: Extraction and Scoring
        for region_id, crop in crops.items():
            if crop is None:
                results.append({
                    "region_id": region_id,
                    "student_response": "AMBIGUOUS",
                    "confidence": "low",
                    "score": "ambiguous",
                    "error": "Crop failed"
                })
                continue
                
            region_config = self.region_defs["regions"].get(region_id, {})
            q_type = region_config.get("type", "fallback")
            
            # Select extractor based on type
            extractor = self.extractors.get(q_type, self.extractors["fallback"])
            
            # Extract
            student_response, confidence = extractor.extract(crop, region_config)
            
            # Score
            answer_entry = self.answer_key.get(region_id, {})
            score_result = self.scorer.score(student_response, answer_entry)
            
            results.append({
                "region_id": region_id,
                "student_response": student_response,
                "confidence": confidence,
                "score": score_result
            })
            
        return results
