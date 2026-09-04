import json
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "backend" / "templates" / "ws_g2_hybrid_w06" / "template_image.jpg"
OUT_DIR = ROOT / "pipeline_stop_obstacles"


def put_wrapped_text(image, lines, origin=(36, 72), scale=0.8, color=(20, 20, 20), thickness=2, line_gap=36):
    x, y = origin
    for line in lines:
        cv2.putText(image, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)
        y += line_gap


def label_image(base, title, subtitle):
    image = base.copy()
    overlay = image.copy()
    cv2.rectangle(overlay, (0, 0), (image.shape[1], 170), (255, 255, 255), -1)
    image = cv2.addWeighted(overlay, 0.82, image, 0.18, 0)
    cv2.rectangle(image, (0, 0), (image.shape[1], 170), (230, 230, 230), 2)
    put_wrapped_text(image, [title, subtitle], origin=(36, 64), scale=0.9, color=(25, 25, 25), thickness=2, line_gap=42)
    return image


def make_card(title, lines, size=(1179, 1487), bg=(248, 248, 248)):
    width, height = size
    image = np.full((height, width, 3), bg, dtype=np.uint8)
    cv2.rectangle(image, (42, 42), (width - 42, height - 42), (60, 100, 150), 4)
    cv2.rectangle(image, (42, 42), (width - 42, 190), (232, 240, 250), -1)
    put_wrapped_text(image, [title], origin=(76, 118), scale=1.15, color=(25, 60, 110), thickness=3, line_gap=46)
    put_wrapped_text(image, lines, origin=(76, 280), scale=0.82, color=(35, 35, 35), thickness=2, line_gap=42)
    return image


def save(path, image):
    cv2.imwrite(str(path), image)


def generate_files():
    OUT_DIR.mkdir(exist_ok=True)
    template = cv2.imread(str(TEMPLATE_PATH))
    if template is None:
        raise RuntimeError(f"Template not found: {TEMPLATE_PATH}")

    outputs = []

    empty_path = OUT_DIR / "step_01_worksheet_image_empty_upload_obstacle.jpg"
    empty_path.write_bytes(b"")
    outputs.append({
        "file": empty_path.name,
        "kind": "actual failing upload payload",
        "expected_stop": "API preflight before Step 1",
        "why": "Upload body is empty, so FastAPI endpoint returns HTTP 400 before OpenCV decode.",
    })
    save(
        OUT_DIR / "step_01_worksheet_image_empty_upload_obstacle_preview.png",
        make_card(
            "Step 1 - Worksheet Image: Empty Upload",
            [
                "Actual obstacle file is 0 bytes, so it cannot be displayed as an image.",
                "Backend API sees: not contents",
                "Result: HTTP 400 - Uploaded worksheet image is empty.",
            ],
        ),
    )

    invalid_path = OUT_DIR / "step_01_worksheet_image_decode_obstacle.jpg"
    invalid_path.write_bytes(b"This is not JPEG or PNG image data. OpenCV imdecode should return None.")
    outputs.append({
        "file": invalid_path.name,
        "kind": "actual failing upload payload",
        "expected_stop": "Step 1 - Worksheet image",
        "why": "File is non-empty but not image bytes, so cv2.imdecode returns None.",
    })
    save(
        OUT_DIR / "step_01_worksheet_image_decode_obstacle_preview.png",
        make_card(
            "Step 1 - Worksheet Image: Decode Failure",
            [
                "Actual obstacle file has .jpg extension but contains plain text bytes.",
                "OpenCV imdecode cannot convert it into an image matrix.",
                "Result: failed at Step 1 - Invalid or unsupported image file.",
            ],
        ),
    )

    no_templates = label_image(
        template,
        "Step 2 - Template Resolution Obstacle",
        "Use this when template config/folder is unavailable on server.",
    )
    cv2.rectangle(no_templates, (120, 250), (1050, 1210), (210, 210, 210), 12)
    put_wrapped_text(
        no_templates,
        [
            "This is not caused by worksheet pixels alone.",
            "It happens when backend has zero readable templates.",
            "Pipeline stops with: No template images are available.",
        ],
        origin=(150, 350),
        scale=0.85,
        color=(40, 40, 40),
        thickness=2,
        line_gap=44,
    )
    save(OUT_DIR / "step_02_template_resolution_no_templates_obstacle.png", no_templates)
    outputs.append({
        "file": "step_02_template_resolution_no_templates_obstacle.png",
        "kind": "visual explanation image",
        "expected_stop": "Step 2 - Template resolution",
        "why": "Requires server/config state: all templates missing/unreadable.",
    })

    small = cv2.resize(template, (320, 404), interpolation=cv2.INTER_AREA)
    save(OUT_DIR / "step_03_image_validation_too_small_obstacle.png", small)
    outputs.append({
        "file": "step_03_image_validation_too_small_obstacle.png",
        "kind": "actual failing worksheet image",
        "expected_stop": "Step 3 - Image validation",
        "why": "Smallest side is below 450 pixels.",
    })

    blurry = cv2.GaussianBlur(template, (91, 91), 0)
    save(OUT_DIR / "step_03_image_validation_blurry_obstacle.png", blurry)
    save(
        OUT_DIR / "step_03_image_validation_blurry_obstacle_preview.png",
        label_image(blurry, "Step 3 - Image Validation Obstacle", "Very blurry worksheet: Laplacian sharpness score drops below threshold."),
    )
    outputs.append({
        "file": "step_03_image_validation_blurry_obstacle.png",
        "kind": "actual failing worksheet image",
        "expected_stop": "Step 3 - Image validation",
        "why": "Laplacian sharpness/blur score is below 45.",
    })

    dark = np.clip(template.astype(np.float32) * 0.12, 0, 255).astype(np.uint8)
    save(OUT_DIR / "step_03_image_validation_too_dark_obstacle.png", dark)
    save(
        OUT_DIR / "step_03_image_validation_too_dark_obstacle_preview.png",
        label_image(dark, "Step 3 - Image Validation Obstacle", "Too dark worksheet: average grayscale brightness goes below 45."),
    )
    outputs.append({
        "file": "step_03_image_validation_too_dark_obstacle.png",
        "kind": "actual failing worksheet image",
        "expected_stop": "Step 3 - Image validation",
        "why": "Average brightness is below 45.",
    })

    bright = np.clip(template.astype(np.float32) * 0.08 + 246, 0, 255).astype(np.uint8)
    bright = label_image(bright, "Step 3 - Image Validation Obstacle", "Too bright worksheet: average grayscale brightness goes above 235.")
    save(OUT_DIR / "step_03_image_validation_too_bright_obstacle.png", bright)
    outputs.append({
        "file": "step_03_image_validation_too_bright_obstacle.png",
        "kind": "actual failing worksheet image",
        "expected_stop": "Step 3 - Image validation",
        "why": "Average brightness is above 235.",
    })

    invalid_schema = label_image(
        template,
        "Step 8 - Structured Output Validation Obstacle",
        "Use this to explain missing/wrong region IDs after extraction locking.",
    )
    cv2.rectangle(invalid_schema, (260, 505), (920, 925), (245, 245, 245), -1)
    put_wrapped_text(
        invalid_schema,
        [
            "This is not a pure image-quality failure.",
            "It means extraction output does not match template contract.",
            "Example: expected q1..q8 but q5 missing.",
            "Pipeline stops at structured-output validation.",
        ],
        origin=(300, 600),
        scale=0.76,
        color=(35, 35, 35),
        thickness=2,
        line_gap=42,
    )
    save(OUT_DIR / "step_08_structured_output_validation_invalid_schema_obstacle.png", invalid_schema)
    outputs.append({
        "file": "step_08_structured_output_validation_invalid_schema_obstacle.png",
        "kind": "visual explanation image",
        "expected_stop": "Step 8 - Structured-output validation",
        "why": "Requires extraction/config/code mismatch, such as missing region IDs.",
    })

    crash = template.copy()
    save(OUT_DIR / "step_any_unexpected_code_error_obstacle.png", crash)
    save(
        OUT_DIR / "step_any_unexpected_code_error_obstacle_preview.png",
        make_card(
            "Any Step - Unexpected Code Error Obstacle",
            [
                "Actual test uses a valid worksheet, then simulates a runtime exception.",
                "This is not caused by normal worksheet content.",
                "Example: extractor crash, bad OpenCV call, missing dependency.",
                "Pipeline catches the exception, marks that step failed, then stops.",
            ],
            bg=(250, 246, 244),
        ),
    )
    outputs.append({
        "file": "step_any_unexpected_code_error_obstacle.png",
        "kind": "visual explanation image",
        "expected_stop": "Any step",
        "why": "Requires runtime exception in one pipeline component.",
    })

    make_contact_sheet()
    (OUT_DIR / "manifest.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    return outputs


def make_contact_sheet():
    image_paths = [
        "step_01_worksheet_image_empty_upload_obstacle_preview.png",
        "step_01_worksheet_image_decode_obstacle_preview.png",
        "step_02_template_resolution_no_templates_obstacle.png",
        "step_03_image_validation_too_small_obstacle.png",
        "step_03_image_validation_blurry_obstacle_preview.png",
        "step_03_image_validation_too_dark_obstacle_preview.png",
        "step_03_image_validation_too_bright_obstacle.png",
        "step_08_structured_output_validation_invalid_schema_obstacle.png",
        "step_any_unexpected_code_error_obstacle_preview.png",
    ]
    thumbs = []
    for name in image_paths:
        img = cv2.imread(str(OUT_DIR / name))
        if img is None:
            continue
        thumb = cv2.resize(img, (300, 380), interpolation=cv2.INTER_AREA)
        cv2.rectangle(thumb, (0, 0), (299, 379), (220, 220, 220), 2)
        thumbs.append((name, thumb))

    cols = 3
    rows = int(np.ceil(len(thumbs) / cols))
    sheet = np.full((rows * 460 + 40, cols * 340 + 40, 3), 255, dtype=np.uint8)
    for idx, (name, thumb) in enumerate(thumbs):
        row, col = divmod(idx, cols)
        x = 20 + col * 340
        y = 20 + row * 460
        sheet[y:y + 380, x:x + 300] = thumb
        short = name.replace("_obstacle", "").replace(".png", "").replace("_preview", "")
        pieces = [short[i:i + 30] for i in range(0, len(short), 30)][:2]
        put_wrapped_text(sheet, pieces, origin=(x, y + 415), scale=0.45, color=(20, 20, 20), thickness=1, line_gap=22)
    cv2.imwrite(str(OUT_DIR / "pipeline_stop_obstacles_contact_sheet.png"), sheet)


if __name__ == "__main__":
    generated = generate_files()
    print(json.dumps(generated, indent=2))
