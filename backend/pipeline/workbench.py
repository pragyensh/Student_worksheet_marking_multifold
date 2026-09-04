import base64
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import requests


TEMPLATE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))


def _region(region_id: str, kind: str, box: List[float], key: str = "", options: Optional[List[List[float]]] = None,
            variants: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "region_id": region_id,
        "type": kind,
        "box": box,
        "correct_value": key,
        "acceptable_variants": variants or [],
        "options": options or [],
    }


TEMPLATES: List[Dict[str, Any]] = [
    {
        "template_id": "ws_g3_subjective_w06",
        "name": "Grade 3 Subjective W06",
        "grade": "Grade 3",
        "mode": "Subjective",
        "template_image": os.path.join(TEMPLATE_ROOT, "ws_g3_subjective_w06", "template_image.jpg"),
        "current_solution": "Manual template config + local CV; Gemini prompt kept only as reference.",
        "regions": [
            _region("q1-match-160", "matching", [0.12, 0.15, 0.88, 0.38], "picture 3"),
            _region("q1-match-195", "matching", [0.12, 0.15, 0.88, 0.38], "picture 4"),
            _region("q2-topleft", "numeral", [0.34, 0.43, 0.46, 0.48], "192"),
            _region("q2-topright", "numeral", [0.73, 0.43, 0.86, 0.48], "150"),
            _region("q2-bottomleft", "numeral", [0.34, 0.56, 0.46, 0.61], "107"),
            _region("q2-bottomright", "numeral", [0.73, 0.56, 0.86, 0.61], "200"),
            _region("q3-row1-number", "numeral", [0.53, 0.67, 0.83, 0.72], "145"),
            _region("q3-row1-blank1", "text", [0.56, 0.735, 0.66, 0.77], "saikda", variants=["sankda", "hundreds"]),
            _region("q3-row1-dahai", "numeral", [0.69, 0.735, 0.75, 0.77], "4"),
            _region("q3-row1-ikai", "numeral", [0.82, 0.735, 0.89, 0.77], "5"),
            _region("q3-row2-number", "numeral", [0.53, 0.80, 0.83, 0.85], "109"),
            _region("q3-row2-dahai", "numeral", [0.62, 0.875, 0.70, 0.91], "10"),
            _region("q3-row2-ikai", "numeral", [0.82, 0.875, 0.89, 0.91], "9"),
        ],
    },
    {
        "template_id": "ws_g3_hybrid_w06",
        "name": "Grade 3 Hybrid W06",
        "grade": "Grade 3",
        "mode": "Hybrid",
        "template_image": os.path.join(TEMPLATE_ROOT, "ws_g3_hybrid_w06", "template_image.jpg"),
        "current_solution": "ORB template resolution + checkbox CV; handwriting boxes flagged for review until model exists.",
        "regions": [
            _region("q1", "mcq", [0.10, 0.16, 0.47, 0.30], "A", options=[[0.13, 0.20, 0.18, 0.24], [0.32, 0.20, 0.37, 0.24]]),
            _region("q2", "mcq", [0.49, 0.15, 0.88, 0.31], "A", options=[[0.50, 0.20, 0.55, 0.24], [0.50, 0.245, 0.55, 0.285], [0.50, 0.29, 0.55, 0.33]]),
            _region("q3", "mcq", [0.10, 0.32, 0.47, 0.47], "A", options=[[0.13, 0.40, 0.18, 0.44], [0.13, 0.445, 0.18, 0.485]]),
            _region("q4", "mcq", [0.50, 0.32, 0.88, 0.47], "A", options=[[0.53, 0.405, 0.58, 0.445], [0.66, 0.405, 0.71, 0.445], [0.53, 0.455, 0.58, 0.495], [0.66, 0.455, 0.71, 0.495]]),
            _region("q5", "mcq", [0.10, 0.49, 0.47, 0.64], "A", options=[[0.13, 0.59, 0.18, 0.63], [0.33, 0.59, 0.38, 0.63], [0.42, 0.59, 0.47, 0.63]]),
            _region("q6", "mcq", [0.50, 0.49, 0.88, 0.64], "B", options=[[0.53, 0.59, 0.58, 0.63], [0.66, 0.59, 0.71, 0.63], [0.80, 0.59, 0.85, 0.63]]),
            _region("q7a", "numeral", [0.24, 0.78, 0.31, 0.83], "192"),
            _region("q7b", "numeral", [0.44, 0.78, 0.52, 0.83], "107"),
            _region("q8a", "numeral", [0.73, 0.78, 0.81, 0.83], "150"),
            _region("q8b", "numeral", [0.90, 0.78, 0.97, 0.83], "200"),
        ],
    },
    {
        "template_id": "ws_g2_subjective_w06",
        "name": "Grade 2 Subjective W06",
        "grade": "Grade 2",
        "mode": "Subjective",
        "template_image": os.path.join(TEMPLATE_ROOT, "ws_g2_subjective_w06", "template_image.jpg"),
        "current_solution": "Manual region map + local mark detection; handwritten/drawing values need a trained recognizer.",
        "regions": [
            _region("q1a-r1", "numeral", [0.37, 0.18, 0.49, 0.23], "32"),
            _region("q1b-r1", "drawing", [0.58, 0.18, 0.67, 0.23], "3"),
            _region("q1b-r2", "drawing", [0.67, 0.18, 0.77, 0.23], "0"),
            _region("q1c-bf1-tens", "numeral", [0.23, 0.33, 0.34, 0.40], "3"),
            _region("q1c-bf1-ones", "numeral", [0.36, 0.33, 0.47, 0.40], "1"),
            _region("q1c-bf2-tens", "numeral", [0.61, 0.33, 0.72, 0.40], "2"),
            _region("q1c-bf2-ones", "numeral", [0.74, 0.33, 0.85, 0.40], "0"),
            _region("q2-pair1-r1", "symbol", [0.26, 0.52, 0.33, 0.58], ">"),
            _region("q2-pair2-r1", "symbol", [0.26, 0.64, 0.33, 0.70], "<"),
            _region("q2-pair3-r1", "symbol", [0.73, 0.52, 0.80, 0.58], "="),
            _region("q2-pair4-r1", "symbol", [0.73, 0.64, 0.80, 0.70], "="),
            _region("q3-row1-mark", "mark", [0.78, 0.73, 0.86, 0.79], "tick"),
            _region("q3-row2-mark", "mark", [0.78, 0.82, 0.86, 0.88], "cross"),
        ],
    },
    {
        "template_id": "ws_g2_hybrid_w06",
        "name": "Grade 2 Hybrid W06",
        "grade": "Grade 2",
        "mode": "Hybrid",
        "template_image": os.path.join(TEMPLATE_ROOT, "ws_g2_hybrid_w06", "template_image.jpg"),
        "current_solution": "Four-sheet template resolver + MCQ checkbox CV; q7/q8 are review until handwriting model exists.",
        "regions": [
            _region("q1", "mcq", [0.10, 0.15, 0.47, 0.30], "A", options=[[0.13, 0.19, 0.18, 0.23], [0.32, 0.19, 0.37, 0.23], [0.13, 0.25, 0.18, 0.29]]),
            _region("q2", "mcq", [0.49, 0.15, 0.87, 0.30], "B", options=[[0.50, 0.25, 0.55, 0.29], [0.63, 0.25, 0.68, 0.29], [0.76, 0.25, 0.81, 0.29]]),
            _region("q3", "mcq", [0.10, 0.31, 0.47, 0.47], "A", options=[[0.13, 0.43, 0.18, 0.47], [0.26, 0.43, 0.31, 0.47], [0.38, 0.43, 0.43, 0.47]]),
            _region("q4", "mcq", [0.49, 0.31, 0.87, 0.47], "B", options=[[0.50, 0.43, 0.55, 0.47], [0.63, 0.43, 0.68, 0.47], [0.76, 0.43, 0.81, 0.47]]),
            _region("q5", "mcq", [0.10, 0.49, 0.47, 0.68], "A", options=[[0.13, 0.64, 0.18, 0.68], [0.26, 0.64, 0.31, 0.68], [0.38, 0.64, 0.43, 0.68]]),
            _region("q6", "mcq", [0.49, 0.49, 0.87, 0.68], "C", options=[[0.50, 0.64, 0.55, 0.68], [0.63, 0.64, 0.68, 0.68], [0.76, 0.64, 0.81, 0.68]]),
            _region("q7", "numeral", [0.36, 0.76, 0.45, 0.84], "32"),
            _region("q8", "drawing", [0.52, 0.76, 0.76, 0.84], "TENS=3; ONES=0"),
        ],
    },
]


STEP_DEFS = [
    ("worksheet_image", "Worksheet image", "backend.api.app", "OpenCV imdecode", "Accept and decode the uploaded worksheet image."),
    ("template_resolution", "Template resolution", "TemplateResolver", "ORB + edge/image similarity", "Identify which of the 4 configured worksheets this upload belongs to."),
    ("image_validation", "Image validation and normalisation gate", "ImageValidator", "Laplacian blur + brightness + size checks", "Reject unreadable, tiny, very dark/bright or badly blurred images."),
    ("normalization", "Page normalisation", "PageNormalizer", "Page contour detection + ORB homography + resize fallback", "Create a stable image for the selected template size."),
    ("response_region_preparation", "Response-region preparation", "RegionCropper", "Manual JSON-style boxes", "Locate and crop every configured answer region."),
    ("response_extraction", "Response extraction", "LocalExtractor", "Red/diff ink mask + checkbox option scoring", "Read only visible student-created marks in each region."),
    ("response_standardization_locking", "Response standardization and locking", "ResponseLocker", "Allowed-value normalization", "Lock outputs as A/B/C/D, BLANK, MULTIPLE, AMBIGUOUS or review-needed values."),
    ("extraction_output_validation", "Structured-output validation", "OutputValidator", "Region ID/order/schema checks", "Confirm the extraction result has exactly the required structure."),
    ("response_scoring", "Response scoring", "DeterministicScorer", "Exact answer-key comparison", "Compare locked responses to answer keys after extraction is locked."),
    ("exception_handling", "Exception handling", "ReviewGate", "State counters", "Flag blank, ambiguous, multiple, low-confidence and unsupported-recognition cases."),
    ("result_aggregation", "Result aggregation", "ResultAggregator", "Correct/total + review summary", "Combine question-level states into the final worksheet result."),
]


def list_templates() -> List[Dict[str, str]]:
    return [
        {
            "template_id": item["template_id"],
            "name": item["name"],
            "grade": item["grade"],
            "mode": item["mode"],
            "current_solution": item["current_solution"],
            "region_count": len(item["regions"]),
        }
        for item in TEMPLATES
    ]


def run_workbench_pipeline(file_bytes: bytes, filename: str, requested_step: int) -> Dict[str, Any]:
    started = time.perf_counter()
    state: Dict[str, Any] = {
        "filename": filename,
        "file_bytes": file_bytes,
        "steps": [],
        "image": None,
        "template": None,
        "template_image": None,
        "normalized_image": None,
        "regions": [],
        "raw_observations": [],
        "locked_responses": [],
        "scored_results": [],
        "exceptions": {},
        "summary": {},
    }

    completed_steps = _compute_all_steps(state)
    target = max(0, min(int(requested_step), len(STEP_DEFS) - 1))
    visible_steps = []
    for index, definition in enumerate(STEP_DEFS):
        if index <= target and index < len(completed_steps):
            visible_steps.append(completed_steps[index])
        else:
            visible_steps.append(_pending_step(index, definition))

    return {
        "filename": filename,
        "requested_step": target,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
        "template": _template_summary(state.get("template")),
        "steps": visible_steps,
        "results": state["scored_results"] if target >= 8 else [],
        "summary": state["summary"] if target >= 10 else {},
    }


def _compute_all_steps(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    steps = []
    for index, definition in enumerate(STEP_DEFS):
        step_started = time.perf_counter()
        try:
            output = _run_step(index, state)
            status = output.pop("_status", "completed")
            errors = output.pop("_errors", [])
            artifacts = output.pop("_artifacts", [])
        except Exception as exc:
            output = {"message": "Step failed before producing an output."}
            status = "failed"
            errors = [str(exc)]
            artifacts = []

        step_id, title, component, algorithm, purpose = definition
        steps.append({
            "index": index,
            "step_id": step_id,
            "title": title,
            "purpose": purpose,
            "component": component,
            "algorithm": algorithm,
            "status": status,
            "input": _step_input(index, state),
            "output": output,
            "errors": errors,
            "duration_ms": round((time.perf_counter() - step_started) * 1000, 1),
            "artifacts": artifacts,
        })

        if status == "failed":
            break

    return steps


def _run_step(index: int, state: Dict[str, Any]) -> Dict[str, Any]:
    if index == 0:
        image = _decode_image(state["file_bytes"])
        state["image"] = image
        h, w = image.shape[:2]
        return {
            "filename": state["filename"],
            "width": w,
            "height": h,
            "channels": image.shape[2] if len(image.shape) == 3 else 1,
            "_artifacts": [_image_artifact("Uploaded worksheet", image)],
        }

    if index == 1:
        match = _resolve_template(state["image"])
        state["template"] = match["template"]
        state["template_image"] = cv2.imread(match["template"]["template_image"])
        return {
            "selected_template": match["template"]["template_id"],
            "selected_name": match["template"]["name"],
            "confidence": match["confidence"],
            "candidates": match["candidates"],
            "_status": "completed" if match["confidence"] != "low" else "warning",
            "_errors": [] if match["confidence"] != "low" else ["Low template-resolution confidence. Review before trusting extraction."],
        }

    if index == 2:
        metrics = _validate_image(state["image"])
        return {
            **metrics,
            "_status": "completed" if metrics["accepted"] else "failed",
            "_errors": metrics["errors"],
        }

    if index == 3:
        normalization = _normalize_to_template(state["image"], state["template_image"])
        normalized = normalization["image"]
        state["normalized_image"] = normalized
        return {
            "normalization": normalization["method"],
            "details": normalization["details"],
            "template_canvas": {
                "width": state["template_image"].shape[1],
                "height": state["template_image"].shape[0],
            },
            "_artifacts": [_image_artifact("Normalized worksheet", normalized)],
        }

    if index == 4:
        regions = _prepare_regions(state["template"], state["normalized_image"])
        state["regions"] = regions
        overlay = _draw_regions(state["normalized_image"], regions)
        crop_artifacts = [_image_artifact(f"Crop {item['region_id']}", item["crop"]) for item in regions[:10]]
        return {
            "region_count": len(regions),
            "regions": [{"region_id": item["region_id"], "type": item["type"], "bbox": item["bbox"]} for item in regions],
            "_artifacts": [_image_artifact("Region overlay", overlay)] + crop_artifacts,
        }

    if index == 5:
        observations = _extract_responses(state["regions"], state["normalized_image"], state["template_image"])
        state["raw_observations"] = observations
        return {
            "observation_count": len(observations),
            "observations": observations,
        }

    if index == 6:
        locked = _lock_responses(state["raw_observations"])
        state["locked_responses"] = locked
        return {
            "locked_count": len(locked),
            "locked_responses": locked,
        }

    if index == 7:
        validation = _validate_output(state["template"], state["locked_responses"])
        return {
            **validation,
            "_status": "completed" if validation["valid"] else "failed",
            "_errors": validation["errors"],
        }

    if index == 8:
        scored = _score(state["template"], state["locked_responses"])
        state["scored_results"] = scored
        return {
            "results": scored,
        }

    if index == 9:
        exceptions = _collect_exceptions(state["scored_results"])
        state["exceptions"] = exceptions
        return exceptions

    summary = _aggregate(state["scored_results"], state["template"], state["exceptions"])
    state["summary"] = summary
    return summary


def _step_input(index: int, state: Dict[str, Any]) -> Dict[str, Any]:
    if index == 0:
        return {"file": state["filename"]}
    if index == 1:
        return {"image": "decoded worksheet image", "template_pool": [item["template_id"] for item in TEMPLATES]}
    if index == 2:
        return {"image": "decoded worksheet image"}
    if index == 3:
        return {"image": "decoded worksheet image", "selected_template": state.get("template", {}).get("template_id")}
    if index == 4:
        return {"normalized_image": "selected template canvas", "region_source": "manual config"}
    if index == 5:
        return {"cropped_regions": len(state.get("regions", []))}
    if index == 6:
        return {"raw_observations": len(state.get("raw_observations", []))}
    if index == 7:
        return {"locked_responses": len(state.get("locked_responses", []))}
    if index == 8:
        return {"locked_responses": len(state.get("locked_responses", [])), "answer_key": "selected template only"}
    if index == 9:
        return {"scored_results": len(state.get("scored_results", []))}
    return {"scored_results": len(state.get("scored_results", [])), "exceptions": state.get("exceptions", {})}


def _pending_step(index: int, definition: Tuple[str, str, str, str, str]) -> Dict[str, Any]:
    step_id, title, component, algorithm, purpose = definition
    return {
        "index": index,
        "step_id": step_id,
        "title": title,
        "purpose": purpose,
        "component": component,
        "algorithm": algorithm,
        "status": "pending",
        "input": {},
        "output": {},
        "errors": [],
        "duration_ms": 0,
        "artifacts": [],
    }


def _decode_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Invalid or unsupported image file.")
    return image


def _resolve_template(image: np.ndarray) -> Dict[str, Any]:
    candidates = []
    for template in TEMPLATES:
        template_image = cv2.imread(template["template_image"])
        if template_image is None:
            continue
        resized = cv2.resize(image, (template_image.shape[1], template_image.shape[0]))
        diff_score = _image_similarity_score(resized, template_image)
        edge_score = _edge_similarity_score(resized, template_image)
        orb_score = _orb_match_score(resized, template_image)
        score = round((diff_score * 0.42) + (edge_score * 0.33) + (orb_score * 0.25), 3)
        candidates.append({
            "template_id": template["template_id"],
            "name": template["name"],
            "score": score,
            "image_similarity": round(diff_score, 3),
            "edge_similarity": round(edge_score, 3),
            "orb_similarity": round(orb_score, 3),
        })

    if not candidates:
        raise ValueError("No template images are available.")

    candidates.sort(key=lambda item: item["score"], reverse=True)
    selected_id = candidates[0]["template_id"]
    selected = next(item for item in TEMPLATES if item["template_id"] == selected_id)
    confidence = "high" if candidates[0]["score"] >= 0.74 else "medium" if candidates[0]["score"] >= 0.55 else "low"
    return {"template": selected, "candidates": candidates, "confidence": confidence}


def _image_similarity_score(image: np.ndarray, template: np.ndarray) -> float:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_image, gray_template)
    return float(max(0.0, 1.0 - (float(np.mean(diff)) / 255.0)))


def _edge_similarity_score(image: np.ndarray, template: np.ndarray) -> float:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    edges_image = cv2.Canny(gray_image, 60, 160)
    edges_template = cv2.Canny(gray_template, 60, 160)
    overlap = np.logical_and(edges_image > 0, edges_template > 0).sum()
    union = np.logical_or(edges_image > 0, edges_template > 0).sum()
    if union == 0:
        return 0.0
    return float(overlap / union)


def _orb_match_score(image: np.ndarray, template: np.ndarray) -> float:
    orb = cv2.ORB_create(nfeatures=1200)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    kp_template, desc_template = orb.detectAndCompute(gray_template, None)
    kp_image, desc_image = orb.detectAndCompute(gray_image, None)
    if desc_template is None or desc_image is None or not kp_template or not kp_image:
        return 0.0
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(desc_template, desc_image)
    if not matches:
        return 0.0
    good = [match for match in matches if match.distance <= 68]
    if len(good) < 8:
        return float(min(len(good) / 80.0, 1.0))

    points_template = np.float32([kp_template[match.queryIdx].pt for match in good]).reshape(-1, 1, 2)
    points_image = np.float32([kp_image[match.trainIdx].pt for match in good]).reshape(-1, 1, 2)
    _, inlier_mask = cv2.findHomography(points_template, points_image, cv2.RANSAC, 5.0)
    inliers = int(inlier_mask.sum()) if inlier_mask is not None else 0
    inlier_ratio = inliers / max(1, len(good))
    inlier_volume = min(inliers / 320.0, 1.0)
    return float((inlier_volume * 0.8) + (inlier_ratio * 0.2))


def _validate_image(image: np.ndarray) -> Dict[str, Any]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    height, width = image.shape[:2]
    errors = []
    if min(width, height) < 450:
        errors.append("Image resolution is too small for reliable region crops.")
    if blur_score < 45:
        errors.append("Image looks blurry. Upload a clearer worksheet photo.")
    if brightness < 45 or brightness > 235:
        errors.append("Image brightness is outside the safe range.")
    return {
        "accepted": not errors,
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 1),
        "brightness": round(brightness, 1),
        "errors": errors,
    }


def _normalize_to_template(image: np.ndarray, template_image: np.ndarray) -> Dict[str, Any]:
    template_height, template_width = template_image.shape[:2]
    target_size = (template_width, template_height)

    page_quad = _detect_page_quad(image)
    if page_quad is not None:
        ordered_quad = _order_points(page_quad)
        if _quad_is_full_frame(ordered_quad, image.shape[1], image.shape[0]):
            aligned = _align_to_template_with_features(image, template_image)
            if aligned is not None:
                return {
                    "image": aligned,
                    "method": "ORB feature homography alignment from full-frame/cropped input",
                    "details": {
                        "page_quad": [[round(float(x), 1), round(float(y), 1)] for x, y in ordered_quad],
                        "target_width": template_width,
                        "target_height": template_height,
                        "warning": "Page boundary is not clearly visible; alignment used internal worksheet features.",
                    },
                }

        destination = np.array([
            [0, 0],
            [template_width - 1, 0],
            [template_width - 1, template_height - 1],
            [0, template_height - 1],
        ], dtype="float32")
        matrix = cv2.getPerspectiveTransform(ordered_quad, destination)
        warped = cv2.warpPerspective(image, matrix, target_size)
        refined = _align_to_template_with_features(warped, template_image)
        output_image = refined if refined is not None else warped
        return {
            "image": output_image,
            "method": "page contour perspective correction + ORB refinement" if refined is not None else "page contour perspective correction",
            "details": {
                "page_quad": [[round(float(x), 1), round(float(y), 1)] for x, y in ordered_quad],
                "target_width": template_width,
                "target_height": template_height,
            },
        }

    aligned = _align_to_template_with_features(image, template_image)
    if aligned is not None:
        return {
            "image": aligned,
            "method": "ORB feature homography alignment",
            "details": {
                "target_width": template_width,
                "target_height": template_height,
            },
        }

    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    return {
        "image": resized,
        "method": "resize fallback to selected template canvas",
        "details": {
            "target_width": template_width,
            "target_height": template_height,
            "reason": "No reliable page contour or feature homography was found.",
        },
    }


def _detect_page_quad(image: np.ndarray) -> Optional[np.ndarray]:
    background_quad = _detect_page_quad_from_background(image)
    if background_quad is not None:
        return background_quad

    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_area = float(width * height)
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:10]:
        area = cv2.contourArea(contour)
        if area < image_area * 0.18 or area > image_area * 0.98:
            continue
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return approx.reshape(4, 2).astype("float32")

    return None


def _detect_page_quad_from_background(image: np.ndarray) -> Optional[np.ndarray]:
    height, width = image.shape[:2]
    border = max(8, min(height, width) // 40)
    corner_samples = np.concatenate([
        image[:border, :border].reshape(-1, 3),
        image[:border, -border:].reshape(-1, 3),
        image[-border:, :border].reshape(-1, 3),
        image[-border:, -border:].reshape(-1, 3),
    ], axis=0)
    background = np.median(corner_samples, axis=0)
    distance = np.linalg.norm(image.astype(np.float32) - background.astype(np.float32), axis=2)
    mask = (distance > 18).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    image_area = float(width * height)
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        area = cv2.contourArea(contour)
        if area < image_area * 0.18 or area > image_area * 0.98:
            continue
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return approx.reshape(4, 2).astype("float32")

        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        rect_area = float(rect[1][0] * rect[1][1])
        if rect_area > image_area * 0.18:
            return box.astype("float32")

    return None


def _align_to_template_with_features(image: np.ndarray, template_image: np.ndarray) -> Optional[np.ndarray]:
    template_height, template_width = template_image.shape[:2]
    orb = cv2.ORB_create(nfeatures=1500)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    kp_template, desc_template = orb.detectAndCompute(gray_template, None)
    kp_image, desc_image = orb.detectAndCompute(gray_image, None)
    if desc_template is None or desc_image is None or len(kp_template) < 12 or len(kp_image) < 12:
        return None

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(desc_template, desc_image), key=lambda item: item.distance)
    good = [match for match in matches if match.distance <= 72][:240]
    if len(good) < 12:
        return None

    points_template = np.float32([kp_template[match.queryIdx].pt for match in good]).reshape(-1, 1, 2)
    points_image = np.float32([kp_image[match.trainIdx].pt for match in good]).reshape(-1, 1, 2)
    matrix, inlier_mask = cv2.findHomography(points_image, points_template, cv2.RANSAC, 5.0)
    inliers = int(inlier_mask.sum()) if inlier_mask is not None else 0
    if matrix is None or inliers < 20:
        return None

    return cv2.warpPerspective(image, matrix, (template_width, template_height))


def _quad_is_full_frame(points: np.ndarray, width: int, height: int) -> bool:
    expected = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ], dtype="float32")
    tolerance = max(width, height) * 0.02
    return bool(np.all(np.linalg.norm(points - expected, axis=1) <= tolerance))


def _order_points(points: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    point_sum = points.sum(axis=1)
    rect[0] = points[np.argmin(point_sum)]
    rect[2] = points[np.argmax(point_sum)]

    point_diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(point_diff)]
    rect[3] = points[np.argmax(point_diff)]
    return rect


def _prepare_regions(template: Dict[str, Any], normalized_image: np.ndarray) -> List[Dict[str, Any]]:
    height, width = normalized_image.shape[:2]
    regions = []
    for config in template["regions"]:
        bbox = _scale_box(config["box"], width, height)
        x1, y1, x2, y2 = bbox
        crop = normalized_image[y1:y2, x1:x2].copy()
        region = dict(config)
        region["bbox"] = bbox
        region["crop"] = crop
        regions.append(region)
    return regions


def _extract_responses(regions: List[Dict[str, Any]], normalized_image: np.ndarray, template_image: np.ndarray) -> List[Dict[str, Any]]:
    observations = []
    height, width = template_image.shape[:2]
    for region in regions:
        template_crop = _crop_box(template_image, region["bbox"])
        crop = region["crop"]
        if region["type"] == "mcq":
            response, confidence, evidence = _extract_mcq(region, normalized_image, template_image, width, height)
        else:
            response, confidence, evidence = _extract_open_region(crop, template_crop, region["type"])
        observations.append({
            "region_id": region["region_id"],
            "type": region["type"],
            "raw_response": response,
            "confidence": confidence,
            "evidence": evidence,
        })
    return observations


def _extract_mcq(region: Dict[str, Any], normalized_image: np.ndarray, template_image: np.ndarray, width: int, height: int) -> Tuple[str, str, Dict[str, Any]]:
    labels = ["A", "B", "C", "D", "E"]
    scores = []
    for index, option_box in enumerate(region.get("options", [])):
        bbox = _scale_box(option_box, width, height)
        option_crop = _crop_box(normalized_image, bbox)
        template_option = _crop_box(template_image, bbox)
        mark = _mark_metrics(option_crop, template_option)
        scores.append({"option": labels[index], **mark})

    red_selected = [item["option"] for item in scores if item["red_pixels"] >= 25]
    selected = red_selected or [item["option"] for item in scores if item["marked"]]
    if len(selected) == 1:
        response = selected[0]
        confidence = "high"
    elif len(selected) > 1:
        response = "MULTIPLE"
        confidence = "low"
    else:
        response = "BLANK"
        confidence = "high"

    return response, confidence, {"selection_mode": "red_ink" if red_selected else "diff_fallback", "option_scores": scores}


def _extract_open_region(crop: np.ndarray, template_crop: np.ndarray, region_type: str) -> Tuple[str, str, Dict[str, Any]]:
    metrics = _mark_metrics(crop, template_crop)
    red_ink_present = metrics["red_pixels"] >= 25
    dark_ink_fallback = metrics["marked"] and metrics["mark_ratio"] >= 0.22 and region_type != "drawing"
    if not red_ink_present and not dark_ink_fallback:
        confidence = "medium" if region_type == "drawing" else "high"
        return "BLANK", confidence, {**metrics, "selection_mode": "red_ink_or_strong_diff"}

    recognized = _recognize_open_response(crop, region_type)
    if recognized:
        return recognized["student_response"], recognized["confidence"], {
            **metrics,
            "selection_mode": "red_ink_or_strong_diff",
            "recognizer": recognized["recognizer"],
            "recognizer_note": recognized["note"],
        }

    return "MARK_PRESENT", "medium", {
        **metrics,
        "selection_mode": "red_ink_or_strong_diff",
        "note": "Visible ink exists, but no handwriting/drawing recognizer is configured.",
    }


def _recognize_open_response(crop: np.ndarray, region_type: str) -> Optional[Dict[str, str]]:
    provider = os.getenv("HANDWRITING_RECOGNIZER", "").strip().lower()
    if provider in ("", "none", "off", "disabled"):
        return None
    if provider == "gemini":
        return _recognize_with_gemini(crop, region_type)
    return None


def _recognize_with_gemini(crop: np.ndarray, region_type: str) -> Optional[Dict[str, str]]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
    prompt = _recognizer_prompt(region_type)
    ok, encoded = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not ok:
        return None

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(encoded.tobytes()).decode("ascii"),
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    try:
        response = requests.post(url, params={"key": api_key}, json=body, timeout=45)
        response.raise_for_status()
        payload = response.json()
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except Exception:
        return None

    student_response = str(parsed.get("student_response", "AMBIGUOUS")).strip()
    confidence = str(parsed.get("confidence", "medium")).strip().lower()
    if confidence not in ("high", "medium", "low"):
        confidence = "medium"

    student_response = _sanitize_recognized_response(student_response, region_type)
    return {
        "student_response": student_response,
        "confidence": confidence,
        "recognizer": f"gemini:{model}",
        "note": str(parsed.get("note", "External recognizer used only after local ink detection."))[:240],
    }


def _recognizer_prompt(region_type: str) -> str:
    shared = (
        "Read only the student's visible handwriting or drawing in this cropped worksheet answer region. "
        "Do not solve the math question. Do not use an answer key. If the visual evidence is unclear, return AMBIGUOUS. "
        "Return only JSON with keys student_response, confidence, and note. Confidence must be high, medium, or low. "
    )
    if region_type == "numeral":
        return shared + "The answer type is a handwritten numeral. Return the digits exactly as visible, or BLANK/AMBIGUOUS."
    if region_type == "symbol":
        return shared + "The answer type is a comparison symbol. Return exactly one of >, <, =, BLANK, or AMBIGUOUS."
    if region_type == "mark":
        return shared + "The answer type is a mark. Return exactly tick, cross, BLANK, or AMBIGUOUS."
    if region_type == "drawing":
        return shared + "The answer type is a base-ten drawing. If clear, return TENS=<number>; ONES=<number>. Otherwise return AMBIGUOUS."
    if region_type == "matching":
        return shared + "The answer type is a matching/selection response. Describe the selected visual target briefly, or return AMBIGUOUS."
    return shared + "Return the transcribed text exactly as visible, or BLANK/AMBIGUOUS."


def _sanitize_recognized_response(value: str, region_type: str) -> str:
    if not value:
        return "AMBIGUOUS"
    upper = value.upper()
    if upper in ("BLANK", "AMBIGUOUS", "STRAY_MARK", "MULTIPLE"):
        return upper
    if region_type == "symbol":
        return value if value in (">", "<", "=") else "AMBIGUOUS"
    if region_type == "mark":
        lowered = value.lower()
        if lowered in ("tick", "cross"):
            return lowered
        return "AMBIGUOUS"
    if region_type == "numeral":
        digits = "".join(ch for ch in value if ch.isdigit())
        return digits or "AMBIGUOUS"
    if region_type == "drawing":
        return value.upper().replace(" ", "")
    return value.strip()


def _lock_responses(observations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    locked = []
    for item in observations:
        raw = item["raw_response"]
        if raw == "MARK_PRESENT":
            student_response = "AMBIGUOUS"
            lock_note = "Ink was detected, but this response type needs a recognizer before it can be converted."
        else:
            student_response = raw
            lock_note = "Locked from visible extraction only; answer key not used."
        locked.append({
            "region_id": item["region_id"],
            "student_response": student_response,
            "confidence": item["confidence"],
            "lock_note": lock_note,
        })
    return locked


def _validate_output(template: Dict[str, Any], locked: List[Dict[str, str]]) -> Dict[str, Any]:
    expected = [item["region_id"] for item in template["regions"]]
    actual = [item["region_id"] for item in locked]
    errors = []
    if actual != expected:
        errors.append("Region order or count does not match the template contract.")
    for item in locked:
        for key in ("region_id", "student_response", "confidence"):
            if key not in item:
                errors.append(f"Missing {key} in {item.get('region_id', 'unknown')}.")
    return {
        "valid": not errors,
        "expected_region_count": len(expected),
        "actual_region_count": len(actual),
        "expected_order": expected,
        "actual_order": actual,
        "errors": errors,
    }


def _score(template: Dict[str, Any], locked: List[Dict[str, str]]) -> List[Dict[str, str]]:
    key_map = {item["region_id"]: item for item in template["regions"]}
    results = []
    for item in locked:
        answer = key_map.get(item["region_id"], {})
        response = item["student_response"]
        if response == "BLANK":
            score = "blank"
        elif response in ("AMBIGUOUS", "STRAY_MARK"):
            score = "ambiguous"
        elif response == "MULTIPLE":
            score = "multiple"
        else:
            response_key = _answer_key(response)
            expected = _answer_key(answer.get("correct_value", ""))
            variants = [_answer_key(value) for value in answer.get("acceptable_variants", [])]
            score = "correct" if response_key == expected or response_key in variants else "incorrect"
        results.append({
            "region_id": item["region_id"],
            "student_response": response,
            "confidence": item["confidence"],
            "correct_value": str(answer.get("correct_value", "")),
            "score": score,
        })
    return results


def _collect_exceptions(results: List[Dict[str, str]]) -> Dict[str, Any]:
    counts = {"blank": 0, "ambiguous": 0, "multiple": 0, "low_confidence": 0}
    review_regions = []
    for item in results:
        if item["score"] in counts:
            counts[item["score"]] += 1
        if item["confidence"] == "low":
            counts["low_confidence"] += 1
        if item["score"] in ("ambiguous", "multiple") or item["confidence"] == "low":
            review_regions.append(item["region_id"])
    return {
        "counts": counts,
        "review_regions": review_regions,
        "manual_review_needed": bool(review_regions),
    }


def _aggregate(results: List[Dict[str, str]], template: Dict[str, Any], exceptions: Dict[str, Any]) -> Dict[str, Any]:
    correct = sum(1 for item in results if item["score"] == "correct")
    total = len(results)
    return {
        "template_id": template["template_id"],
        "template_name": template["name"],
        "correct": correct,
        "total": total,
        "score_label": f"{correct}/{total}",
        "manual_review_needed": exceptions.get("manual_review_needed", False),
        "review_regions": exceptions.get("review_regions", []),
        "notes": "MCQs and blank states are local-CV based; marked open answers use the configured recognizer, otherwise they are flagged for review.",
    }


def _answer_key(value: Any) -> str:
    return "".join(str(value).strip().lower().split())


def _mark_metrics(crop: np.ndarray, template_crop: np.ndarray) -> Dict[str, Any]:
    if crop.size == 0:
        return {"marked": False, "red_pixels": 0, "changed_pixels": 0, "mark_ratio": 0.0}
    if template_crop.shape[:2] != crop.shape[:2]:
        template_crop = cv2.resize(template_crop, (crop.shape[1], crop.shape[0]))
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    template_hsv = cv2.cvtColor(template_crop, cv2.COLOR_BGR2HSV)
    red_mask_1 = cv2.inRange(hsv, (0, 45, 60), (14, 255, 255))
    red_mask_2 = cv2.inRange(hsv, (165, 45, 60), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)
    template_red_mask_1 = cv2.inRange(template_hsv, (0, 45, 60), (14, 255, 255))
    template_red_mask_2 = cv2.inRange(template_hsv, (165, 45, 60), (180, 255, 255))
    template_red_mask = cv2.bitwise_or(template_red_mask_1, template_red_mask_2)
    red_mask = cv2.bitwise_and(red_mask, cv2.bitwise_not(template_red_mask))
    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template_crop, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_crop, gray_template)
    _, diff_mask = cv2.threshold(diff, 55, 255, cv2.THRESH_BINARY)
    changed_pixels = int(cv2.countNonZero(diff_mask))
    red_pixels = int(cv2.countNonZero(red_mask))
    area = max(1, crop.shape[0] * crop.shape[1])
    mark_ratio = (changed_pixels + red_pixels) / area
    marked = red_pixels > max(6, area * 0.003) or changed_pixels > max(12, area * 0.015)
    return {
        "marked": bool(marked),
        "red_pixels": red_pixels,
        "changed_pixels": changed_pixels,
        "mark_ratio": round(float(mark_ratio), 4),
    }


def _scale_box(box: List[float], width: int, height: int) -> List[int]:
    x1, y1, x2, y2 = box
    return [
        max(0, min(width, int(round(x1 * width)))),
        max(0, min(height, int(round(y1 * height)))),
        max(0, min(width, int(round(x2 * width)))),
        max(0, min(height, int(round(y2 * height)))),
    ]


def _relative_bbox(parent: List[int], child: List[int]) -> List[int]:
    return [child[0] - parent[0], child[1] - parent[1], child[2] - parent[0], child[3] - parent[1]]


def _crop_box(image: np.ndarray, box: List[int]) -> np.ndarray:
    h, w = image.shape[:2]
    x1, y1, x2, y2 = box
    x1 = max(0, min(w, x1))
    x2 = max(0, min(w, x2))
    y1 = max(0, min(h, y1))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return image[0:0, 0:0].copy()
    return image[y1:y2, x1:x2].copy()


def _draw_regions(image: np.ndarray, regions: List[Dict[str, Any]]) -> np.ndarray:
    overlay = image.copy()
    for index, region in enumerate(regions):
        x1, y1, x2, y2 = region["bbox"]
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (20, 145, 255), 2)
        cv2.putText(overlay, str(index + 1), (x1 + 4, max(18, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 145, 255), 2)
    return overlay


def _image_artifact(title: str, image: np.ndarray) -> Dict[str, str]:
    if image is None or image.size == 0:
        return {"title": title, "type": "image", "data_url": ""}
    display = image.copy()
    height, width = display.shape[:2]
    max_width = 760
    if width > max_width:
        scale = max_width / width
        display = cv2.resize(display, (max_width, int(height * scale)), interpolation=cv2.INTER_AREA)
    ok, encoded = cv2.imencode(".jpg", display, [int(cv2.IMWRITE_JPEG_QUALITY), 78])
    if not ok:
        return {"title": title, "type": "image", "data_url": ""}
    data = base64.b64encode(encoded.tobytes()).decode("ascii")
    return {"title": title, "type": "image", "data_url": f"data:image/jpeg;base64,{data}"}


def _template_summary(template: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not template:
        return None
    return {
        "template_id": template["template_id"],
        "name": template["name"],
        "grade": template["grade"],
        "mode": template["mode"],
        "region_count": len(template["regions"]),
        "current_solution": template["current_solution"],
    }
