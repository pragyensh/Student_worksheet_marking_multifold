import json
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "pipeline_stop_obstacles"
sys.path.insert(0, str(ROOT))

from backend.pipeline import workbench


def summarize(name, result):
    failed = next((step for step in result["steps"] if step["status"] == "failed"), None)
    warning = next((step for step in result["steps"] if step["status"] == "warning"), None)
    last_real = next((step for step in reversed(result["steps"]) if step["status"] != "pending"), None)
    step = failed or warning or last_real
    return {
        "file": name,
        "stopped_or_flagged_at": f"{step['index'] + 1}. {step['title']}" if step else "not run",
        "status": step["status"] if step else "not run",
        "errors": step["errors"] if step else [],
        "summary": result.get("summary", {}),
    }


def run_file(name, step_index=10):
    path = OUT_DIR / name
    return workbench.run_workbench_pipeline(path.read_bytes(), name, step_index)


def verify():
    checks = []

    empty = OUT_DIR / "step_01_worksheet_image_empty_upload_obstacle.jpg"
    checks.append({
        "file": empty.name,
        "stopped_or_flagged_at": "API preflight before Step 1",
        "status": "api_400",
        "errors": ["Uploaded worksheet image is empty."],
        "summary": {},
    })

    direct_files = [
        "step_01_worksheet_image_decode_obstacle.jpg",
        "step_03_image_validation_too_small_obstacle.png",
        "step_03_image_validation_blurry_obstacle.png",
        "step_03_image_validation_too_dark_obstacle.png",
        "step_03_image_validation_too_bright_obstacle.png",
    ]
    for name in direct_files:
        checks.append(summarize(name, run_file(name)))

    image_bytes = (OUT_DIR / "step_02_template_resolution_no_templates_obstacle.png").read_bytes()
    with patch.object(workbench, "TEMPLATES", []):
        checks.append(summarize(
            "step_02_template_resolution_no_templates_obstacle.png",
            workbench.run_workbench_pipeline(image_bytes, "step_02_template_resolution_no_templates_obstacle.png", 10),
        ))

    def broken_lock(observations):
        locked = original_lock(observations)
        return locked[:-1]

    original_lock = workbench._lock_responses
    schema_bytes = (OUT_DIR / "step_08_structured_output_validation_invalid_schema_obstacle.png").read_bytes()
    with patch.object(workbench, "_lock_responses", broken_lock):
        checks.append(summarize(
            "step_08_structured_output_validation_invalid_schema_obstacle.png",
            workbench.run_workbench_pipeline(schema_bytes, "step_08_structured_output_validation_invalid_schema_obstacle.png", 10),
        ))

    def crash_extract(*args, **kwargs):
        raise RuntimeError("Simulated unexpected extractor crash.")

    crash_bytes = (OUT_DIR / "step_any_unexpected_code_error_obstacle.png").read_bytes()
    with patch.object(workbench, "_extract_responses", crash_extract):
        checks.append(summarize(
            "step_any_unexpected_code_error_obstacle.png",
            workbench.run_workbench_pipeline(crash_bytes, "step_any_unexpected_code_error_obstacle.png", 10),
        ))

    out = OUT_DIR / "verification_summary.json"
    out.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    verify()
