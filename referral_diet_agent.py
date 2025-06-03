from base_agent import Agent, run_server
from typing import Dict, Any, Optional, List, Tuple
import re

class ReferralAndDietAgent(Agent):
    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(endpoint)
        self.specialist_database = self._initialize_specialist_database()
        self.diet_recommendations = self._initialize_diet_recommendations()

    def _initialize_specialist_database(self) -> Dict[str, Dict[str, str]]:
        return {
            "heart": {
                "specialist": "Cardiologist",
                "when_to_refer": ["chest pain", "shortness of breath", "palpitations", "high blood pressure"],
                "urgency": "Urgent - Schedule within 1-2 weeks"
            },
            "joints": {
                "specialist": "Rheumatologist",
                "when_to_refer": ["joint pain", "swelling", "morning stiffness", "arthritis"],
                "urgency": "Non-urgent - Schedule within 4-6 weeks"
            },
            "skin": {
                "specialist": "Dermatologist",
                "when_to_refer": ["rash", "skin changes", "suspicious moles", "severe acne"],
                "urgency": "Routine - Schedule within 4-8 weeks"
            },
            "digestive": {
                "specialist": "Gastroenterologist",
                "when_to_refer": ["abdominal pain", "chronic diarrhea", "blood in stool", "acid reflux"],
                "urgency": "Semi-urgent - Schedule within 2-4 weeks"
            },
            "brain": {
                "specialist": "Neurologist",
                "when_to_refer": ["headaches", "dizziness", "numbness", "seizures"],
                "urgency": "Varies - Depends on symptoms"
            }
        }

    def _initialize_diet_recommendations(self) -> Dict[str, Dict[str, Any]]:
        return {
            "heart": {
                "recommended": ["fruits", "vegetables", "whole grains", "lean proteins", "fish"],
                "avoid": ["saturated fats", "excess salt", "processed foods"],
                "tips": [
                    "Follow a Mediterranean-style diet",
                    "Limit red meat consumption",
                    "Choose low-sodium options",
                    "Include omega-3 rich foods"
                ]
            },
            "diabetes": {
                "recommended": ["high-fiber foods", "lean proteins", "healthy fats", "low-glycemic carbs"],
                "avoid": ["sugary drinks", "processed snacks", "white bread", "candy"],
                "tips": [
                    "Monitor carbohydrate intake",
                    "Eat regular, balanced meals",
                    "Choose whole grains over refined grains",
                    "Include protein with each meal"
                ]
            },
            "digestive": {
                "recommended": ["yogurt", "fiber-rich foods", "cooked vegetables", "lean proteins"],
                "avoid": ["spicy foods", "fatty foods", "caffeine", "alcohol"],
                "tips": [
                    "Eat smaller, frequent meals",
                    "Stay well hydrated",
                    "Chew food thoroughly",
                    "Avoid lying down after meals"
                ]
            },
            "general": {
                "recommended": ["fruits", "vegetables", "whole grains", "lean proteins"],
                "avoid": ["excess sugar", "processed foods", "excessive alcohol"],
                "tips": [
                    "Stay hydrated",
                    "Eat a variety of colorful foods",
                    "Practice portion control",
                    "Listen to your body's hunger cues"
                ]
            }
        }

    def get_specialist_referral(self, symptoms: str) -> Dict[str, str]:
        symptoms_lower = symptoms.lower()
        referrals = []

        for system, data in self.specialist_database.items():
            if any(symptom in symptoms_lower for symptom in data["when_to_refer"]):
                referrals.append({
                    "specialist": data["specialist"],
                    "urgency": data["urgency"],
                    "reason": f"Based on reported symptoms: {', '.join(s for s in data['when_to_refer'] if s in symptoms_lower)}"
                })

        return referrals

    def get_diet_recommendations(self, symptoms: str) -> Dict[str, Any]:
        symptoms_lower = symptoms.lower()
        
        # Map symptoms to condition categories
        if any(s in symptoms_lower for s in ["chest pain", "high blood pressure", "heart"]):
            return self.diet_recommendations["heart"]
        elif any(s in symptoms_lower for s in ["blood sugar", "diabetes", "thirst"]):
            return self.diet_recommendations["diabetes"]
        elif any(s in symptoms_lower for s in ["stomach", "digestive", "nausea"]):
            return self.diet_recommendations["digestive"]
        else:
            return self.diet_recommendations["general"]

    def handle(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Extract and clean text
        if isinstance(content, dict) and 'text' in content:
            input_text = content['text']
        else:
            input_text = str(content)
            
        input_text = input_text.replace('\\n', '\n').strip()
        
        if not input_text.strip():
            return self.format_response("No symptoms provided for analysis.")

        # Extract symptoms and medical history
        symptoms_match = re.search(r'Symptoms:\s*([^\n]+)', input_text, re.IGNORECASE)
        history_match = re.search(r'Medical History:\s*([^\n]+)', input_text, re.IGNORECASE)
        
        if not symptoms_match:
            return self.format_response("No symptoms found in the input text.")
            
        symptoms = symptoms_match.group(1).strip()
        medical_history = history_match.group(1).strip() if history_match else ""
        
        # Combine symptoms and medical history for analysis
        analysis_text = f"{symptoms} {medical_history}"

        # Get specialist referrals
        referrals = self.get_specialist_referral(analysis_text)
        diet_recs = self.get_diet_recommendations(analysis_text)

        # Format the output
        output = "Referral and Diet Recommendations:\n\n"

        if referrals:
            output += "Specialist Referrals:\n"
            for ref in referrals:
                output += (
                    f"- {ref['specialist']}\n"
                    f"  Urgency: {ref['urgency']}\n"
                    f"  Reason: {ref['reason']}\n\n"
                )
        else:
            output += "No immediate specialist referrals needed based on reported symptoms.\n\n"

        output += "Dietary Recommendations:\n"
        output += "Recommended Foods:\n- " + "\n- ".join(diet_recs["recommended"]) + "\n\n"
        output += "Foods to Avoid:\n- " + "\n- ".join(diet_recs["avoid"]) + "\n\n"
        output += "Dietary Tips:\n- " + "\n- ".join(diet_recs["tips"]) + "\n\n"

        # Add medical history context if available
        if medical_history and medical_history.lower() != 'none':
            output += f"Note: These recommendations take into account your medical history of: {medical_history}\n\n"

        output += (
            "Important: These are general recommendations. Please consult with a healthcare "
            "provider for personalized advice based on your specific condition."
        )

        return self.format_response(output)

if __name__ == "__main__":
    agent = ReferralAndDietAgent()
    run_server(agent, port=5004) 