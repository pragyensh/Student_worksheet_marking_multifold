# Worksheet Variation Testing Log

Template: `ws_g3_subjective_w06` / Grade 3 Subjective W06.
Region count: 13.

## Generated Variations

1. `01_ws_g3_subjective_w06_blank_original.png`
   - Purpose: Blank original template.
2. `02_ws_g3_subjective_w06_fully_filled_correct.png`
   - Purpose: All configured regions filled with correct synthetic answers.
3. `03_ws_g3_subjective_w06_fully_filled_incorrect.png`
   - Purpose: All configured regions filled with intentionally wrong synthetic answers.
4. `04_ws_g3_subjective_w06_half_filled_correct.png`
   - Purpose: First half of regions filled correctly; remaining regions blank.
5. `05_ws_g3_subjective_w06_alternate_filled_correct.png`
   - Purpose: Alternating regions filled correctly; skipped regions blank.
6. `06_ws_g3_subjective_w06_mcq_only_correct.png`
   - Purpose: Only MCQ regions filled correctly.
7. `07_ws_g3_subjective_w06_open_only_correct.png`
   - Purpose: Only handwritten/open regions filled correctly.
8. `08_ws_g3_subjective_w06_multiple_marks.png`
   - Purpose: MCQ regions receive multiple selections where possible.
9. `09_ws_g3_subjective_w06_stray_marks.png`
   - Purpose: Correct worksheet plus stray red marks outside answer regions.
10. `10_ws_g3_subjective_w06_tedha_rotated.png`
   - Purpose: Rotated worksheet to test deskew/perspective normalization.
11. `11_ws_g3_subjective_w06_perspective_skewed.png`
   - Purpose: Perspective-skewed worksheet to test page contour correction.
12. `12_ws_g3_subjective_w06_zoomed_cropped.png`
   - Purpose: Zoomed/cropped worksheet with page boundary partly missing.
13. `13_ws_g3_subjective_w06_blurry.png`
   - Purpose: Blurry worksheet expected to fail validation.
14. `14_ws_g3_subjective_w06_small.png`
   - Purpose: Small low-resolution worksheet expected to fail validation.
15. `15_ws_g3_subjective_w06_too_dark.png`
   - Purpose: Very dark worksheet expected to fail brightness validation.

## Handwriting/Open-Answer Plan

- MCQ extraction stays local through red-ink and diff-based checkbox CV.
- Handwriting/drawing/symbol/matching crops are sent to an external recognizer only if local CV first detects visible student ink.
- Default external recognizer hook: `HANDWRITING_RECOGNIZER=gemini`, `GEMINI_API_KEY=<key>`, optional `GEMINI_MODEL=gemini-3.5-flash-lite`.
- If no API key is configured, open answers remain `AMBIGUOUS` instead of pretending to read handwriting.

## Pipeline Run Results

- `01_ws_g3_subjective_w06_blank_original.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195
- `02_ws_g3_subjective_w06_fully_filled_correct.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `03_ws_g3_subjective_w06_fully_filled_incorrect.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `04_ws_g3_subjective_w06_half_filled_correct.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright
- `05_ws_g3_subjective_w06_alternate_filled_correct.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-bottomleft, q3-row1-number, q3-row1-dahai, q3-row2-number, q3-row2-ikai
- `06_ws_g3_subjective_w06_mcq_only_correct.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195
- `07_ws_g3_subjective_w06_open_only_correct.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `08_ws_g3_subjective_w06_multiple_marks.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195
- `09_ws_g3_subjective_w06_stray_marks.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `10_ws_g3_subjective_w06_tedha_rotated.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `completed`
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `11_ws_g3_subjective_w06_perspective_skewed.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `warning`
  - Stop/warning step: 2. Template resolution
  - Errors: Low template-resolution confidence. Review before trusting extraction.
  - Step 4 normalization: page contour perspective correction + ORB refinement
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `12_ws_g3_subjective_w06_zoomed_cropped.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `warning`
  - Stop/warning step: 2. Template resolution
  - Errors: Low template-resolution confidence. Review before trusting extraction.
  - Step 4 normalization: ORB feature homography alignment from full-frame/cropped input
  - Score: 0/13
  - Review regions: q1-match-160, q1-match-195, q2-topleft, q2-topright, q2-bottomleft, q2-bottomright, q3-row1-number, q3-row1-blank1, q3-row1-dahai, q3-row1-ikai, q3-row2-number, q3-row2-dahai, q3-row2-ikai
- `13_ws_g3_subjective_w06_blurry.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `failed`
  - Stop/warning step: 3. Image validation and normalisation gate
  - Errors: Image looks blurry. Upload a clearer worksheet photo.
- `14_ws_g3_subjective_w06_small.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `failed`
  - Stop/warning step: 3. Image validation and normalisation gate
  - Errors: Image resolution is too small for reliable region crops.
- `15_ws_g3_subjective_w06_too_dark.png`
  - Selected template: `ws_g3_subjective_w06`
  - Final status: `failed`
  - Stop/warning step: 3. Image validation and normalisation gate
  - Errors: Image brightness is outside the safe range.
