from pydantic import BaseModel, Field
from typing import Optional

class HistoryTile(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="""REQUIRED: The exact title or concise summary of the feedback item being tracked.

        TITLE REQUIREMENTS:
        - Extract the precise title from previous feedback (strength spotlight or wisdom whisper)
        - Use the same language and terminology as the original feedback
        - Keep it concise while maintaining the essential meaning
        - Focus on the core skill or behavior being tracked
        
        EXAMPLES:
        - "Evidence Depth Enhancement" (from previous wisdom whisper)
        - "Systematic Problem Analysis" (from previous strength spotlight)
        - "Alternative Perspective Integration" (from previous feedback)
        
        CONSISTENCY REQUIREMENT:
        - Maintain consistency with how feedback was originally titled
        - Preserve the specific language used in previous assessments
        - Ensure the title clearly connects to the tracked feedback item"""
    )
    
    hasImplemented: Optional[bool] = Field(
        default=None, 
        description="""REQUIRED: Assess whether this specific feedback has been implemented in the current workout.

        IMPLEMENTATION ASSESSMENT PROCESS:
        1. REVIEW ORIGINAL FEEDBACK: Examine the complete previous feedback including:
           - Title: The main topic or skill area
           - Detail: The specific explanation of what was needed
           - Next Steps: The actionable recommendations provided
           - Reflection Question: The self-monitoring guidance given
        
        2. ANALYZE CURRENT WORKOUT: Look for evidence in current responses of:
           - Behavioral changes that align with previous recommendations
           - Application of specific strategies or approaches suggested
           - Improvement in the identified skill or area
           - Evidence that they considered or applied the reflection question
        
        3. IMPLEMENTATION CRITERIA:
           - TRUE: Clear evidence that user has reasonably addressed this feedback
             * Shows behavioral change consistent with recommendations
             * Demonstrates application of suggested strategies
             * Exhibits improvement in the identified area
             * Indicates they've internalized and acted on the guidance
           
           - FALSE: Little or no evidence of implementation
             * Same patterns or limitations persist
             * No clear application of recommended strategies
             * Minimal progress in the identified area
             * Appears to have not considered or applied the feedback
        
        ASSESSMENT STANDARDS:
        - Base decision on observable evidence from current workout responses
        - Look for "reasonable degree" of implementation, not perfection
        - Consider the difficulty and complexity of the feedback being implemented
        - Focus on meaningful progress rather than complete mastery
        - Compare current behavior patterns with previous assessment"""
    )

    model_config = {
        "arbitrary_types_allowed": True
    }