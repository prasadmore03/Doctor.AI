import re
from typing import Dict, Any, Optional
import requests

class Agent:
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint

    def handle(self, content: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method")

    def format_response(self, text: str, response_type: str = "text") -> Dict[str, Any]:
        return {
            "content": {
                "type": response_type,
                "text": text
            }
        }

    def call_external_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.endpoint:
            raise ValueError("No endpoint configured for external service call")
        
        try:
            response = requests.post(self.endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return self.format_response(f"Error calling external service: {str(e)}")

def run_server(agent: Agent, host: str = "127.0.0.1", port: int = 5000):
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "agent_type": agent.__class__.__name__})

    @app.route('/a2a', methods=['POST'])
    def handle_request():
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Invalid request"}), 400
        try:
            result = agent.handle(data)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    app.run(host=host, port=port) 