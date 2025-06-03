from base_agent import Agent, run_server
from typing import Dict, Any, Optional, List, Tuple
import re

class MedicationAgent(Agent):
    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(endpoint)
        self.medication_database = self._initialize_medication_database()

    def _initialize_medication_database(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "pain": [
                {
                    "name": "Acetaminophen",
                    "usage": "For mild to moderate pain",
                    "precautions": "Do not exceed recommended dose. Avoid alcohol.",
                    "common_brands": ["Tylenol", "Paracetamol"]
                },
                {
                    "name": "Ibuprofen",
                    "usage": "For pain and inflammation",
                    "precautions": "Take with food. Not recommended for stomach ulcers.",
                    "common_brands": ["Advil", "Motrin"]
                }
            ],
            "allergy": [
                {
                    "name": "Cetirizine",
                    "usage": "For allergies and hay fever",
                    "precautions": "May cause drowsiness",
                    "common_brands": ["Zyrtec"]
                },
                {
                    "name": "Loratadine",
                    "usage": "For allergies",
                    "precautions": "Non-drowsy formula",
                    "common_brands": ["Claritin"]
                }
            ],
            "fever": [
                {
                    "name": "Acetaminophen",
                    "usage": "For fever reduction",
                    "precautions": "Do not exceed recommended dose",
                    "common_brands": ["Tylenol", "Paracetamol"]
                },
                {
                    "name": "Ibuprofen",
                    "usage": "For fever and inflammation",
                    "precautions": "Take with food",
                    "common_brands": ["Advil", "Motrin"]
                }
            ],
            "cough": [
                {
                    "name": "Dextromethorphan",
                    "usage": "For dry cough",
                    "precautions": "May cause drowsiness",
                    "common_brands": ["Robitussin", "Delsym"]
                },
                {
                    "name": "Guaifenesin",
                    "usage": "For wet/productive cough",
                    "precautions": "Drink plenty of water",
                    "common_brands": ["Mucinex"]
                }
            ]
        }

    def suggest_medications(self, symptoms: str) -> List[Dict[str, Any]]:
        symptoms_lower = symptoms.lower()
        suggestions = []
        
        # Map symptoms to medication categories
        symptom_categories = {
            "pain": ["pain", "ache", "headache", "migraine"],
            "allergy": ["allergy", "sneez", "itch", "rash"],
            "fever": ["fever", "temperature", "hot"],
            "cough": ["cough", "chest", "congestion"]
        }
        
        # Find matching categories based on symptoms
        matched_categories = []
        for category, keywords in symptom_categories.items():
            if any(keyword in symptoms_lower for keyword in keywords):
                matched_categories.append(category)
        
        # Get medication suggestions for each matched category
        for category in matched_categories:
            if category in self.medication_database:
                suggestions.extend(self.medication_database[category])
        
        return suggestions

    def handle(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Extract and clean text
        if isinstance(content, dict) and 'text' in content:
            input_text = content['text']
        else:
            input_text = str(content)
            
        input_text = input_text.replace('\\n', '\n').strip()
        
        if not input_text.strip():
            return self.format_response("No symptoms provided for medication suggestions.")
        
        # Extract symptoms from the text
        symptoms_match = re.search(r'Symptoms:\s*([^\n]+)', input_text, re.IGNORECASE)
        if not symptoms_match:
            return self.format_response("No symptoms found in the input text.")
            
        symptoms = symptoms_match.group(1).strip()
        
        # Get medication suggestions
        medications = self.suggest_medications(symptoms)
        
        if not medications:
            return self.format_response(
                "No specific over-the-counter medications can be suggested for these symptoms. "
                "Please consult a healthcare provider for appropriate treatment."
            )
        
        # Format the output
        output = "Medication Suggestions:\n\n"
        for med in medications:
            output += (
                f"Medication: {med['name']}\n"
                f"Usage: {med['usage']}\n"
                f"Common Brands: {', '.join(med['common_brands'])}\n"
                f"Important Precautions: {med['precautions']}\n\n"
            )
        
        # Add medical history and allergies warning if present
        allergies_match = re.search(r'Allergies:\s*([^\n]+)', input_text, re.IGNORECASE)
        if allergies_match and allergies_match.group(1).strip().lower() != 'none':
            output += f"\nCAUTION: Patient has reported allergies: {allergies_match.group(1)}\n"
            output += "Verify all medications against patient's allergy profile.\n\n"
        
        output += (
            "IMPORTANT NOTES:\n"
            "1. These are general suggestions for over-the-counter medications only.\n"
            "2. Always consult a healthcare provider before starting any medication.\n"
            "3. Check for allergies and drug interactions before use.\n"
            "4. Follow package instructions for dosing."
        )
        
        return self.format_response(output)

if __name__ == "__main__":
    agent = MedicationAgent()
    run_server(agent, port=5003) 