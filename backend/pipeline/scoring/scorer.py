from typing import Dict, Any, Union
import json

class DeterministicScorer:
    """
    Scoring module that operates STRICTLY on the locked extracted response.
    It performs deterministic rule-based comparison against the answer key.
    No ML models are used here.
    """
    
    def score(self, student_response: str, answer_entry: Dict[str, Any]) -> str:
        """
        Scores the student response against the answer key.
        
        Args:
            student_response: The exact string extracted by the extraction module.
            answer_entry: The region's answer key entry containing 'correct_value' and 'acceptable_variants'.
            
        Returns:
            "correct", "incorrect", "blank", "ambiguous", or "multiple".
        """
        # Handle special extraction states
        if student_response == "BLANK":
            return "blank"
        if student_response == "AMBIGUOUS" or student_response == "STRAY_MARK":
            return "ambiguous"
        if student_response == "MULTIPLE":
            return "multiple"
            
        if student_response == "MISSING_MODEL" or student_response == "MISSING_API_KEY":
            return "system_error"
            
        correct_value = str(answer_entry.get("correct_value", ""))
        acceptable_variants = [str(v) for v in answer_entry.get("acceptable_variants", [])]
        
        # Check for structured responses (like tens and ones)
        if answer_entry.get("type") == "structured_drawing":
            return self._score_structured(student_response, correct_value)
            
        # Standard string comparison
        # Remove whitespace and lowercase for basic normalization, though for MCQs/math it should be exact
        norm_student = student_response.strip().lower()
        norm_correct = correct_value.strip().lower()
        norm_variants = [v.strip().lower() for v in acceptable_variants]
        
        if norm_student == norm_correct or norm_student in norm_variants:
            return "correct"
            
        return "incorrect"
        
    def _score_structured(self, student_response_json: str, correct_value_json: str) -> str:
        """
        Scores structured JSON responses (e.g. {"tens": 3, "ones": 0})
        """
        try:
            student_data = json.loads(student_response_json)
            correct_data = json.loads(correct_value_json)
            
            # Simple exact match of dictionaries
            if student_data == correct_data:
                return "correct"
            return "incorrect"
        except json.JSONDecodeError:
            return "ambiguous"
