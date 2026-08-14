import os
import json
import cv2
import argparse
from typing import Dict, List, Any
from backend.pipeline.orchestrator import PipelineOrchestrator

def load_ground_truth(gt_path: str) -> List[Dict[str, Any]]:
    """Loads ground truth JSON file."""
    if not os.path.exists(gt_path):
        return []
    with open(gt_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_benchmark(template_id: str, image_dir: str, gt_path: str):
    print(f"Starting benchmark for template {template_id}")
    
    orchestrator = PipelineOrchestrator(template_id)
    ground_truth_data = load_ground_truth(gt_path)
    
    if not ground_truth_data:
        print(f"No ground truth data found at {gt_path}")
        return
        
    total_regions = 0
    correct_extractions = 0
    false_corrections = 0  # CRITICAL METRIC
    
    # Process each test image
    for item in ground_truth_data:
        image_name = item.get("image")
        image_path = os.path.join(image_dir, image_name)
        
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue
            
        img = cv2.imread(image_path)
        if img is None:
            continue
            
        print(f"Processing {image_name}...")
        results = orchestrator.process_image(img)
        
        # Compare with ground truth
        expected_responses = {req["region_id"]: req["expected_extraction"] for req in item.get("regions", [])}
        
        for result in results:
            region_id = result["region_id"]
            extracted = result["student_response"]
            expected = expected_responses.get(region_id)
            
            if expected is None:
                continue
                
            total_regions += 1
            
            # Did we extract what was visibly there?
            if extracted == expected:
                correct_extractions += 1
            else:
                # Was it a false correction? (Extracted matches answer key, but ground truth says student wrote something else)
                # This happens if the model ignored visual evidence and output the right answer
                answer_entry = orchestrator.answer_key.get(region_id, {})
                correct_val = answer_entry.get("correct_value", "")
                
                # If ground truth != correct answer (student was wrong)
                # AND extraction == correct answer (system "corrected" it)
                if str(expected) != str(correct_val) and str(extracted) == str(correct_val):
                    false_corrections += 1
                    print(f"  🚨 FALSE CORRECTION on {region_id}: student wrote {expected}, system extracted {extracted}")
                else:
                    print(f"  ❌ Extraction error on {region_id}: expected {expected}, got {extracted}")
                    
    print("\n--- Benchmark Results ---")
    if total_regions > 0:
        print(f"Total regions evaluated: {total_regions}")
        print(f"Extraction Accuracy: {(correct_extractions/total_regions)*100:.2f}% ({correct_extractions}/{total_regions})")
        print(f"False-Correction Rate: {(false_corrections/total_regions)*100:.2f}% ({false_corrections}/{total_regions})")
        print("Note: False-Correction Rate should be 0.00%")
    else:
        print("No valid regions evaluated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pipeline benchmark")
    parser.add_argument("--template", type=str, default="week_07", help="Template ID")
    parser.add_argument("--images", type=str, default="backend/benchmark/ground_truth/images", help="Directory of test images")
    parser.add_argument("--gt", type=str, default="backend/benchmark/ground_truth/labels.json", help="Path to ground truth labels")
    args = parser.parse_args()
    
    run_benchmark(args.template, args.images, args.gt)
