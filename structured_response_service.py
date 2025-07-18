from models.BrainScanResult import BrainScanResult
from google import genai
import json

class StructuredResponseService:
    def __init__(self):
        pass
    
    def generate_structured_response(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Just fill this out with random placeholder data, set the scan_id to 1",
            config={
                "response_mime_type": "application/json",
                "response_schema": BrainScanResult,
            },
        )
        my_brain_scan_result = response.parsed
        return my_brain_scan_result
    
if __name__ == "__main__":
    structured_response_service = StructuredResponseService()
    res = structured_response_service.generate_structured_response()
    
    print(res)