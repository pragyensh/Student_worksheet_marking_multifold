import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.pipeline.workbench import TEMPLATES, run_workbench_pipeline


VARIATION_ROOT = ROOT / "template_variation_tests"


def summarize_result(path: Path) -> Dict[str, Any]:
    result = run_workbench_pipeline(path.read_bytes(), path.name, 10)
    failed = next((step for step in result["steps"] if step["status"] == "failed"), None)
    warning = next((step for step in result["steps"] if step["status"] == "warning"), None)
    normalization = result["steps"][3] if len(result["steps"]) > 3 else None
    return {
        "file": path.name,
        "path": str(path.relative_to(ROOT)),
        "selected_template": result["template"]["template_id"] if result.get("template") else None,
        "final_status": "failed" if failed else "warning" if warning else "completed",
        "stop_or_warning_step": (
            f"{failed['index'] + 1}. {failed['title']}" if failed
            else f"{warning['index'] + 1}. {warning['title']}" if warning
            else None
        ),
        "errors": (failed or warning or {}).get("errors", []),
        "normalization": normalization["output"] if normalization and normalization["status"] != "pending" else {},
        "summary": result.get("summary", {}),
        "responses": [
            {
                "region_id": item["region_id"],
                "student_response": item["student_response"],
                "score": item["score"],
            }
            for item in result.get("results", [])
        ],
    }


def run_template(template_id: str) -> List[Dict[str, Any]]:
    variation_dir = VARIATION_ROOT / template_id
    files = sorted(variation_dir.glob("*.png"))
    files = [item for item in files if not item.name.endswith("_contact_sheet.png")]
    results = [summarize_result(path) for path in files]
    (variation_dir / "variation_run_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    append_notes(variation_dir, results)
    return results


def append_notes(variation_dir: Path, results: List[Dict[str, Any]]) -> None:
    note_path = variation_dir / "TESTING_NOTES.md"
    lines = note_path.read_text(encoding="utf-8").rstrip().splitlines()
    if "## Pipeline Run Results" in lines:
        lines = lines[:lines.index("## Pipeline Run Results")]
    lines.extend(["", "## Pipeline Run Results", ""])
    for item in results:
        lines.append(f"- `{item['file']}`")
        lines.append(f"  - Selected template: `{item['selected_template']}`")
        lines.append(f"  - Final status: `{item['final_status']}`")
        if item["stop_or_warning_step"]:
            lines.append(f"  - Stop/warning step: {item['stop_or_warning_step']}")
        if item["errors"]:
            lines.append(f"  - Errors: {'; '.join(item['errors'])}")
        method = item.get("normalization", {}).get("normalization")
        if method:
            lines.append(f"  - Step 4 normalization: {method}")
        score = item.get("summary", {}).get("score_label")
        if score:
            lines.append(f"  - Score: {score}")
        review_regions = item.get("summary", {}).get("review_regions")
        if review_regions:
            lines.append(f"  - Review regions: {', '.join(review_regions)}")
    note_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    all_results = []
    for template in TEMPLATES:
        all_results.extend(run_template(template["template_id"]))

    summary = {
        "total_variations": len(all_results),
        "completed": sum(1 for item in all_results if item["final_status"] == "completed"),
        "warnings": sum(1 for item in all_results if item["final_status"] == "warning"),
        "failed": sum(1 for item in all_results if item["final_status"] == "failed"),
        "by_template": {},
    }
    for template in TEMPLATES:
        template_id = template["template_id"]
        rows = [item for item in all_results if Path(item["path"]).parts[1] == template_id]
        summary["by_template"][template_id] = {
            "total": len(rows),
            "completed": sum(1 for item in rows if item["final_status"] == "completed"),
            "warnings": sum(1 for item in rows if item["final_status"] == "warning"),
            "failed": sum(1 for item in rows if item["final_status"] == "failed"),
        }

    (VARIATION_ROOT / "all_variation_run_results.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    (VARIATION_ROOT / "all_variation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
