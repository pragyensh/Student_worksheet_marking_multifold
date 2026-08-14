import json
import os
from typing import Dict, Any

def load_region_definitions(template_id: str, templates_dir: str = "backend/templates") -> Dict[str, Any]:
    """
    Loads region definitions (bounding boxes, types) from a JSON file
    associated with the given template ID.
    """
    json_path = os.path.join(templates_dir, template_id, "regions.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Region definitions not found for template {template_id} at {json_path}")
        
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
