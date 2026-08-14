Student Worksheet Automated Marking System

An image-processing and automated evaluation pipeline for Grade 2–3 government-school mathematics worksheets. Teachers photograph completed worksheets on mobile phones; the system extracts exactly what a student wrote, ticked, or drew, and scores it against a per-worksheet answer key.

Built for MultifoldAI.

Core Principle

Extraction and scoring are treated as two separate problems, solved by two separate stages:

Student marks B → Visual Extraction → "B" → Response Locked → Compare with Answer Key → Correct / Incorrect

Observe → Lock → Score. The pipeline first determines what the student actually marked or wrote, using visual evidence only. Once a response is locked, it is never revised based on what the "correct" answer should be. This avoids a known failure mode in vision-language models — over-correction — where a model silently replaces a student's wrong answer with the mathematically expected one before ever reporting it. No extraction step has access to the answer key; scoring is a separate, deterministic, rule-based comparison with no model involved.

Overall Workflow
Student Worksheet Image (Upload/Input)
        │
        ▼
Page Detection ─────────────── detect worksheet boundary
        │
        ▼
Perspective Correction ──────── convert to top-down view
        │
        ▼
Template Alignment ──────────── align with reference sheet
        │
        ▼
Region-wise Cropping ────────── Q1 → Q8 answer areas
        │
        ▼
Question-specific Extraction ── MCQ / Numeral / Symbol / OCR
        │
        ▼
Response Locking ────────────── extract what student marked
        │
        ▼
Deterministic Scoring ───────── compare with answer key
        │
        ▼
Results & Score ─────────────── question-wise + confidence
Tech Stack
Layer	Technology	Purpose
Frontend	React 19	Worksheet upload and results interface
Frontend tooling	Vite	Development/build environment
Backend	Python 3.10 + FastAPI	API and pipeline orchestration
Server	Uvicorn	Running the FastAPI application
Computer vision	OpenCV	Page detection, thresholding, feature extraction
Numerical processing	NumPy	Image-array and numerical operations
Image processing	OpenCV / Pillow	Image loading and preprocessing
Data validation	Pydantic	API/data validation
Configuration	JSON	Region definitions and answer keys
Template matching	ORB + BFMatcher	Feature-based template alignment
Testing	pytest	Backend testing
VLM/OCR (planned)	Gemini Flash	Fallback extraction for ambiguous visual responses
Question-wise Pipeline (week_07 template)
Questions	Type	Extraction method
Q1–Q6	MCQ	OpenCV-based checkbox/mark detection
Q7	Handwritten numeral	Dedicated handwritten numeral recognition model
Q8	Comparison symbol	Dedicated <, >, = recognition model
MCQ Detection Approach

Classical computer vision, not a general-purpose ML model:

Grayscale conversion
Adaptive thresholding
Segmentation according to the expected option layout
Dark-pixel / fill-ratio analysis
Identification of selected option(s)
Handling of BLANK, MULTIPLE, STRAY_MARK, and AMBIGUOUS cases

This keeps the MCQ pipeline interpretable and fully deterministic — no vision model in the loop.

Handwriting / VLM Approach
Cropped Answer Area → Image Preprocessing → Handwriting/VLM Recognition → Locked Response → Deterministic Score

Interfaces exist for handwritten-numeral, comparison-symbol, Devanagari, and fallback-VLM extraction. Model inference/API integration for some of these is still in progress. Any VLM fallback call is scoped to a single cropped region only and never receives the answer key.

Template-based Architecture

Each worksheet is represented as a self-contained template configuration, so new worksheets can be added without restructuring the pipeline:

backend/templates/week_07/
├── template_image.jpg   # reference layout for alignment
├── regions.json          # location + type of each answer region
└── answer_key.json       # expected answer per region
Repository Structure
/backend
  /pipeline
    preprocessing/   # page detection, perspective correction, alignment
    extraction/       # one module per response type (MCQ, numeral, symbol, OCR, drawings)
    scoring/           # deterministic comparison logic — no ML
  /templates          # per-worksheet template_image.jpg, regions.json, answer_key.json
  /api                 # FastAPI app exposing endpoints to the frontend
  /benchmark            # benchmark harness + accuracy/latency/cost metrics
  /tests
  requirements.txt

/frontend
  # React 19 + Vite — worksheet upload and results interface
  # talks to the backend only via the API layer; performs no extraction/scoring itself

Frontend and backend are kept fully separate — no shared source files or config.

Current Status

Implemented / Operational

React/Vite frontend
FastAPI backend
Worksheet upload API
Page detection
Perspective correction
Template-based region configuration
Initial MCQ extraction pipeline
Deterministic scoring architecture
Question-wise result generation
Confidence representation

Under Development / Validation

Robust template alignment
Improved handwritten checkbox detection
Handwritten numeral recognition
Comparison-symbol recognition
Devanagari handwriting/OCR
Gemini/VLM fallback integration
Ambiguity handling
Accuracy benchmarking and validation
Getting Started
bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
Metrics Tracked (Benchmark Harness)
Extraction accuracy
False-correction rate — a wrong student answer silently changed to the correct one (primary metric)
Blank-vs-faint-handwriting accuracy
Ambiguity handling
MCQ accuracy (including MULTIPLE / BLANK)
Latency per stage
Cost per worksheet (for any paid API path)
License

Proprietary — MultifoldAI internal project.
