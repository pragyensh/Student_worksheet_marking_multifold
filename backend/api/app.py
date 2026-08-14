from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.pipeline.orchestrator import PipelineOrchestrator

app = FastAPI(title="Worksheet Extraction API")

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load orchestrators (in a real app, lazily load or cache these)
orchestrators = {
    "week_07": PipelineOrchestrator("week_07")
}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/process-worksheet")
async def process_worksheet(
    file: UploadFile = File(...),
    template_id: str = Form("week_07")
):
    """
    Endpoint to process a worksheet image and return extracted responses and scores.
    """
    if template_id not in orchestrators:
        # Try to load it
        try:
            orchestrators[template_id] = PipelineOrchestrator(template_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Template {template_id} not found or invalid: {str(e)}")
            
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Invalid image file")
            
        # Run pipeline
        orchestrator = orchestrators[template_id]
        results = orchestrator.process_image(img)
        
        return {
            "template_id": template_id,
            "filename": file.filename,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
