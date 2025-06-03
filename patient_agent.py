from base_agent import Agent, run_server
import re
from typing import Dict, Any, Optional

class PatientDataAgent(Agent):
    def __init__(self, endpoint: Optional[str] = None):
        super().__init__(endpoint)
        self.fields = {
            'name': [r'Patient Name:\s*([^\n]+)', r'Name:\s*([^\n]+)'],
            'age': [r'Age:\s*(\d+)'],
            'weight': [r'Weight:\s*([^\n]+)'],
            'height': [r'Height:\s*([^\n]+)'],
            'symptoms': [r'Symptoms:\s*([^\n]+(?:\n(?!(?:Medical History|Allergies|Current Medications):)[^\n]+)*)', r'Current Problems:\s*([^\n]+(?:\n(?!(?:Medical History|Allergies|Current Medications):)[^\n]+)*)'],
            'medical_history': [r'Medical History:\s*([^\n]+(?:\n(?!(?:Symptoms|Allergies|Current Medications):)[^\n]+)*)'],
            'allergies': [r'Allergies:\s*([^\n]+(?:\n(?!(?:Medical History|Symptoms|Current Medications):)[^\n]+)*)'],
            'medications': [r'Current Medications:\s*([^\n]+(?:\n(?!(?:Medical History|Allergies|Symptoms):)[^\n]+)*)']
        }

    def clean_extracted_text(self, text: str) -> str:
        """Clean extracted text by removing duplicates and formatting properly."""
        if text == 'N/A':
            return text
            
        # Split by lines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        # Join with proper formatting
        if len(unique_lines) == 1:
            return unique_lines[0]
        return '\n'.join(f"{line}" for line in unique_lines)

    def extract_field(self, text: str, patterns: list) -> str:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                extracted_text = match.group(1).strip()
                return self.clean_extracted_text(extracted_text)
        return 'N/A'

    def format_field(self, field_name: str, value: str) -> str:
        """Format a field value for output."""
        if value == 'N/A':
            return f"{field_name}: N/A"
            
        if '\n' in value:
            # For multiline values, format with proper indentation
            lines = value.split('\n')
            return f"{field_name}:\n" + '\n'.join(f"- {line}" for line in lines)
        return f"{field_name}: {value}"

    def handle(self, content: Dict[str, Any]) -> Dict[str, Any]:
        # Extract text from content
        if isinstance(content, dict) and 'text' in content:
            input_text = content['text']
        else:
            input_text = str(content)
            
        # Clean the input text
        input_text = input_text.replace('\\n', '\n').strip()
        
        # Extract all fields
        extracted_data = {
            field: self.extract_field(input_text, patterns)
            for field, patterns in self.fields.items()
        }

        # Format the output with better structure
        output_sections = [
            "Patient Summary:",
            self.format_field("Name", extracted_data['name']),
            self.format_field("Age", extracted_data['age']),
            self.format_field("Weight", extracted_data['weight']),
            self.format_field("Height", extracted_data['height']),
            self.format_field("Symptoms", extracted_data['symptoms']),
            self.format_field("Medical History", extracted_data['medical_history']),
            self.format_field("Allergies", extracted_data['allergies']),
            self.format_field("Current Medications", extracted_data['medications'])
        ]

        output = '\n'.join(output_sections)
        return self.format_response(output)

if __name__ == "__main__":
    agent = PatientDataAgent()
    run_server(agent, port=5001) 