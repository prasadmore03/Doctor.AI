from base_agent import Agent, run_server
from typing import Dict, Any, Optional, List, Tuple
import re

class DiagnosticAgent(Agent):
    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(endpoint)
        self.conditions = self._initialize_conditions()

    def _initialize_conditions(self) -> List[Tuple[List[str], str, str]]:
        return [
            (
                ["chest pain", "shortness of breath"],
                "Possible cardiovascular condition requiring immediate attention",
                "URGENT: Seek emergency medical care immediately. These symptoms could indicate a serious heart condition."
            ),
            (
                ["fever", "cough", "fatigue", "loss of taste", "loss of smell"],
                "Possible respiratory infection",
                "Self-isolate and contact healthcare provider for testing and evaluation."
            ),
            (
                ["headache", "nausea", "sensitivity to light", "visual disturbances"],
                "Possible migraine condition",
                "Rest in a dark, quiet room. Take prescribed migraine medication if available. If symptoms persist or worsen, consult a neurologist."
            ),
            (
                ["joint pain", "swelling", "morning stiffness", "fatigue"],
                "Possible inflammatory arthritis",
                "Schedule an appointment with a rheumatologist. Keep track of affected joints and timing of symptoms."
            ),
            (
                ["abdominal pain", "nausea", "vomiting", "diarrhea"],
                "Possible gastrointestinal condition",
                "Stay hydrated, rest, and follow the BRAT diet. Seek medical attention if symptoms persist or worsen."
            ),
            (
                ["increased thirst", "frequent urination", "fatigue", "blurred vision"],
                "Possible diabetes",
                "Schedule an appointment for blood sugar testing. Monitor fluid intake and urination frequency."
            ),
            (
                ["rash", "itching", "swelling", "difficulty breathing"],
                "Possible allergic reaction",
                "URGENT: If breathing is affected, seek emergency care. Otherwise, take antihistamines and monitor symptoms."
            ),
            (
                ["dizziness", "balance problems", "hearing changes", "ringing in ears"],
                "Possible inner ear or vestibular condition",
                "Consult an ENT specialist. Avoid sudden movements and keep track of trigger factors."
            )
        ]

    def analyze_symptoms(self, symptoms: str) -> Dict[str, str]:
        symptoms_lower = symptoms.lower()
        matched_conditions = []
        
        for condition_symptoms, diagnosis, recommendation in self.conditions:
            if any(symptom in symptoms_lower for symptom in condition_symptoms):
                matched_conditions.append({
                    "matching_symptoms": [s for s in condition_symptoms if s in symptoms_lower],
                    "diagnosis": diagnosis,
                    "recommendation": recommendation
                })
        
        if not matched_conditions:
            return {
                "diagnosis": "Non-specific symptoms detected",
                "recommendation": "Please consult a healthcare provider for a thorough evaluation."
            }
        
        # If multiple conditions match, combine their information
        if len(matched_conditions) > 1:
            return {
                "diagnosis": "Multiple conditions possible: " + 
                           "; ".join(c["diagnosis"] for c in matched_conditions),
                "recommendation": "IMPORTANT: Multiple health concerns identified. " +
                                "Please seek medical attention for a comprehensive evaluation."
            }
        
        return {
            "diagnosis": matched_conditions[0]["diagnosis"],
            "recommendation": matched_conditions[0]["recommendation"]
        }

    def handle(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Extract and clean text
        if isinstance(content, dict) and 'text' in content:
            input_text = content['text']
        else:
            input_text = str(content)
            
        input_text = input_text.replace('\\n', '\n').strip()
        
        if not input_text.strip():
            return self.format_response("No symptoms provided for analysis.")
        
        # Extract symptoms from the text
        symptoms_match = re.search(r'Symptoms:\s*([^\n]+)', input_text, re.IGNORECASE)
        if symptoms_match:
            symptoms = symptoms_match.group(1).strip()
        else:
            return self.format_response("No symptoms found in the input text.")
        
        analysis = self.analyze_symptoms(symptoms)
        output = (
            f"Diagnostic Analysis:\n\n"
            f"Assessment: {analysis['diagnosis']}\n\n"
            f"Recommendations: {analysis['recommendation']}\n\n"
            f"Note: This is an automated analysis and should not replace professional medical advice."
        )
        
        return self.format_response(output)

if __name__ == "__main__":
    agent = DiagnosticAgent()
    run_server(agent, port=5002) 