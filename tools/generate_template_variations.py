import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.pipeline.workbench import TEMPLATES


OUT_ROOT = ROOT / "template_variation_tests"
LABELS = ["A", "B", "C", "D", "E"]


def scale_box(box: List[float], width: int, height: int) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height)


def draw_tick(image: np.ndarray, box: List[float], color=(0, 0, 230), thickness=5) -> None:
    height, width = image.shape[:2]
    x1, y1, x2, y2 = scale_box(box, width, height)
    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    p1 = (x1 + int(w * 0.18), y1 + int(h * 0.55))
    p2 = (x1 + int(w * 0.42), y1 + int(h * 0.78))
    p3 = (x1 + int(w * 0.82), y1 + int(h * 0.22))
    cv2.line(image, p1, p2, color, thickness, cv2.LINE_AA)
    cv2.line(image, p2, p3, color, thickness, cv2.LINE_AA)


def draw_cross(image: np.ndarray, box: List[float], color=(0, 0, 230), thickness=5) -> None:
    height, width = image.shape[:2]
    x1, y1, x2, y2 = scale_box(box, width, height)
    cv2.line(image, (x1 + 5, y1 + 5), (x2 - 5, y2 - 5), color, thickness, cv2.LINE_AA)
    cv2.line(image, (x2 - 5, y1 + 5), (x1 + 5, y2 - 5), color, thickness, cv2.LINE_AA)


def draw_text(image: np.ndarray, text: str, box: List[float], color=(0, 0, 210), scale=1.1, thickness=4) -> None:
    height, width = image.shape[:2]
    x1, y1, _x2, y2 = scale_box(box, width, height)
    baseline = max(y1 + 24, y2 - 10)
    cv2.putText(image, text[:18], (x1 + 8, baseline), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def draw_base_ten(image: np.ndarray, value: str, box: List[float], color=(0, 0, 210)) -> None:
    match = re.search(r"TENS=(\d+)\s*;\s*ONES=(\d+)", value, flags=re.IGNORECASE)
    if not match:
        draw_text(image, value, box, color=color, scale=0.85, thickness=3)
        return
    tens = int(match.group(1))
    ones = int(match.group(2))
    height, width = image.shape[:2]
    x1, y1, _x2, y2 = scale_box(box, width, height)
    x = x1 + 12
    for _ in range(tens):
        cv2.line(image, (x, y1 + 12), (x, y2 - 12), color, 5, cv2.LINE_AA)
        x += 14
    x += 18
    y = y1 + 18
    for index in range(ones):
        cx = x + (index % 6) * 14
        cy = y + (index // 6) * 14
        cv2.circle(image, (cx, cy), 5, color, -1, cv2.LINE_AA)


def correct_option_index(region: Dict[str, Any]) -> int:
    key = str(region.get("correct_value", "")).upper()
    if key in LABELS:
        return LABELS.index(key)
    return 0


def wrong_option_index(region: Dict[str, Any]) -> int:
    options = region.get("options", [])
    if len(options) < 2:
        return 0
    return (correct_option_index(region) + 1) % len(options)


def wrong_value(region: Dict[str, Any]) -> str:
    value = str(region.get("correct_value", "")).strip()
    kind = region["type"]
    if kind == "numeral":
        digits = "".join(ch for ch in value if ch.isdigit())
        if not digits:
            return "9"
        return str(int(digits) + 1)
    if kind == "symbol":
        return {"<": ">", ">": "<", "=": ">"}.get(value, "?")
    if kind == "mark":
        return "cross" if value.lower() == "tick" else "tick"
    if kind == "drawing":
        return "TENS=1; ONES=1"
    if kind == "matching":
        return "wrong"
    return "wrong"


def fill_region(image: np.ndarray, region: Dict[str, Any], mode: str) -> None:
    if region["type"] == "mcq":
        options = region.get("options", [])
        if not options:
            return
        if mode == "multiple":
            draw_tick(image, options[0])
            draw_tick(image, options[min(1, len(options) - 1)])
        elif mode == "wrong":
            draw_tick(image, options[wrong_option_index(region)])
        else:
            draw_tick(image, options[correct_option_index(region)])
        return

    box = region["box"]
    value = str(region.get("correct_value", ""))
    if mode == "wrong":
        value = wrong_value(region)

    if region["type"] == "drawing":
        draw_base_ten(image, value, box)
    elif region["type"] == "mark":
        if value.lower() == "cross":
            draw_cross(image, box)
        else:
            draw_tick(image, box)
    else:
        draw_text(image, value, box)


def fill_regions(image: np.ndarray, template: Dict[str, Any], selector: str, mode: str = "correct") -> np.ndarray:
    regions = template["regions"]
    for index, region in enumerate(regions):
        if selector == "all":
            fill_region(image, region, mode)
        elif selector == "half" and index < max(1, len(regions) // 2):
            fill_region(image, region, mode)
        elif selector == "alternate" and index % 2 == 0:
            fill_region(image, region, mode)
        elif selector == "mcq" and region["type"] == "mcq":
            fill_region(image, region, mode)
        elif selector == "open" and region["type"] != "mcq":
            fill_region(image, region, mode)
    return image


def add_stray_marks(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    cv2.line(image, (int(width * 0.10), int(height * 0.12)), (int(width * 0.20), int(height * 0.14)), (0, 0, 230), 5, cv2.LINE_AA)
    cv2.circle(image, (int(width * 0.90), int(height * 0.72)), 18, (0, 0, 230), 4, cv2.LINE_AA)
    return image


def rotate_canvas(image: np.ndarray, angle: float) -> np.ndarray:
    height, width = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_LINEAR, borderValue=(255, 255, 255))


def perspective_canvas(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    canvas = np.full((height + 260, width + 260, 3), 238, dtype=np.uint8)
    src = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
    dst = np.array([[150, 55], [width + 72, 170], [width + 15, height + 210], [82, height + 55]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(image, matrix, (canvas.shape[1], canvas.shape[0]), borderValue=(238, 238, 238))
    mask = cv2.warpPerspective(np.full((height, width), 255, dtype=np.uint8), matrix, (canvas.shape[1], canvas.shape[0]))
    canvas[mask > 0] = warped[mask > 0]
    return canvas


def zoom_crop(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    cropped = image[int(height * 0.06):int(height * 0.94), int(width * 0.06):int(width * 0.94)]
    return cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)


def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
    return np.clip(image.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def build_variations(template: Dict[str, Any], image: np.ndarray) -> List[Tuple[str, np.ndarray, str]]:
    correct = fill_regions(image.copy(), template, "all", "correct")
    wrong = fill_regions(image.copy(), template, "all", "wrong")
    half = fill_regions(image.copy(), template, "half", "correct")
    mcq_only = fill_regions(image.copy(), template, "mcq", "correct")
    open_only = fill_regions(image.copy(), template, "open", "correct")
    multiple = fill_regions(image.copy(), template, "mcq", "multiple")
    alternate = fill_regions(image.copy(), template, "alternate", "correct")
    stray = add_stray_marks(correct.copy())

    template_id = template["template_id"]
    small_height = max(360, int(360 * image.shape[0] / image.shape[1]))
    return [
        (f"01_{template_id}_blank_original.png", image.copy(), "Blank original template."),
        (f"02_{template_id}_fully_filled_correct.png", correct, "All configured regions filled with correct synthetic answers."),
        (f"03_{template_id}_fully_filled_incorrect.png", wrong, "All configured regions filled with intentionally wrong synthetic answers."),
        (f"04_{template_id}_half_filled_correct.png", half, "First half of regions filled correctly; remaining regions blank."),
        (f"05_{template_id}_alternate_filled_correct.png", alternate, "Alternating regions filled correctly; skipped regions blank."),
        (f"06_{template_id}_mcq_only_correct.png", mcq_only, "Only MCQ regions filled correctly."),
        (f"07_{template_id}_open_only_correct.png", open_only, "Only handwritten/open regions filled correctly."),
        (f"08_{template_id}_multiple_marks.png", multiple, "MCQ regions receive multiple selections where possible."),
        (f"09_{template_id}_stray_marks.png", stray, "Correct worksheet plus stray red marks outside answer regions."),
        (f"10_{template_id}_tedha_rotated.png", rotate_canvas(correct.copy(), -8), "Rotated worksheet to test deskew/perspective normalization."),
        (f"11_{template_id}_perspective_skewed.png", perspective_canvas(correct.copy()), "Perspective-skewed worksheet to test page contour correction."),
        (f"12_{template_id}_zoomed_cropped.png", zoom_crop(correct.copy()), "Zoomed/cropped worksheet with page boundary partly missing."),
        (f"13_{template_id}_blurry.png", cv2.GaussianBlur(correct.copy(), (51, 51), 0), "Blurry worksheet expected to fail validation."),
        (f"14_{template_id}_small.png", cv2.resize(correct.copy(), (360, small_height), interpolation=cv2.INTER_AREA), "Small low-resolution worksheet expected to fail validation."),
        (f"15_{template_id}_too_dark.png", adjust_brightness(correct.copy(), 0.15), "Very dark worksheet expected to fail brightness validation."),
    ]


def make_contact_sheet(out_dir: Path, template_id: str, manifest: List[Dict[str, str]]) -> None:
    thumbs = []
    for item in manifest:
        img = cv2.imread(str(out_dir / item["file"]))
        thumb = cv2.resize(img, (220, 280), interpolation=cv2.INTER_AREA)
        cv2.rectangle(thumb, (0, 0), (219, 279), (210, 210, 210), 2)
        thumbs.append((item["file"], thumb))

    cols = 5
    rows = 3
    sheet = np.full((rows * 360 + 30, cols * 255 + 30, 3), 255, dtype=np.uint8)
    for index, (filename, thumb) in enumerate(thumbs):
        row, col = divmod(index, cols)
        x = 15 + col * 255
        y = 15 + row * 360
        sheet[y:y + 280, x:x + 220] = thumb
        label = filename.replace(f"_{template_id}_", "_").replace("_", " ").replace(".png", "")
        chunks = [label[i:i + 25] for i in range(0, len(label), 25)][:2]
        for line_index, chunk in enumerate(chunks):
            cv2.putText(sheet, chunk, (x, y + 312 + line_index * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (25, 25, 25), 1, cv2.LINE_AA)
    cv2.imwrite(str(out_dir / f"{template_id}_variations_contact_sheet.png"), sheet)


def write_notes(out_dir: Path, template: Dict[str, Any], manifest: List[Dict[str, str]]) -> None:
    lines = [
        "# Worksheet Variation Testing Log",
        "",
        f"Template: `{template['template_id']}` / {template['name']}.",
        f"Region count: {len(template['regions'])}.",
        "",
        "## Generated Variations",
        "",
    ]
    for index, item in enumerate(manifest, start=1):
        lines.append(f"{index}. `{item['file']}`")
        lines.append(f"   - Purpose: {item['purpose']}")
    lines.extend([
        "",
        "## Handwriting/Open-Answer Plan",
        "",
        "- MCQ extraction stays local through red-ink and diff-based checkbox CV.",
        "- Handwriting/drawing/symbol/matching crops are sent to an external recognizer only if local CV first detects visible student ink.",
        "- Default external recognizer hook: `HANDWRITING_RECOGNIZER=gemini`, `GEMINI_API_KEY=<key>`, optional `GEMINI_MODEL=gemini-3.5-flash-lite`.",
        "- If no API key is configured, open answers remain `AMBIGUOUS` instead of pretending to read handwriting.",
    ])
    (out_dir / "TESTING_NOTES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    all_manifest = []
    for template in TEMPLATES:
        template_id = template["template_id"]
        template_image = cv2.imread(template["template_image"])
        if template_image is None:
            raise RuntimeError(f"Missing template image for {template_id}: {template['template_image']}")

        out_dir = OUT_ROOT / template_id
        out_dir.mkdir(parents=True, exist_ok=True)
        for old_file in out_dir.glob("*"):
            if old_file.is_file() and old_file.suffix.lower() in (".png", ".json", ".md"):
                old_file.unlink()
        manifest = []
        for filename, image, purpose in build_variations(template, template_image):
            cv2.imwrite(str(out_dir / filename), image)
            manifest.append({"file": filename, "template": template_id, "purpose": purpose})

        make_contact_sheet(out_dir, template_id, manifest)
        write_notes(out_dir, template, manifest)
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        all_manifest.extend({"path": str((out_dir / item["file"]).relative_to(ROOT)), **item} for item in manifest)

    (OUT_ROOT / "all_variations_manifest.json").write_text(json.dumps(all_manifest, indent=2), encoding="utf-8")
    print(json.dumps({"templates": len(TEMPLATES), "variations": len(all_manifest)}, indent=2))


if __name__ == "__main__":
    main()
