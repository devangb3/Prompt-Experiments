from models.BrainWorkoutResult import BrainWorkoutResult
from google import genai
from logging_config import get_logger

logger = get_logger("structured_response_service")


class StructuredResponseService:
    def __init__(self):
        logger.debug("StructuredResponseService initialized")
    
    def generate_structured_response(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Just fill this out with random placeholder data, set the scan_id to 1",
            config={
                "response_mime_type": "application/json",
                "response_schema": BrainWorkoutResult,
            },
        )
        my_brain_workout_result = response.parsed
        logger.debug(f"Generated structured response: {my_brain_workout_result}")
        return my_brain_workout_result
    
if __name__ == "__main__":
    structured_response_service = StructuredResponseService()
    res = structured_response_service.generate_structured_response()
    
    logger.info(f"Structured response result: {res}")