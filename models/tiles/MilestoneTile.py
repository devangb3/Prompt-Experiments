from pydantic import BaseModel, Field
from typing import Optional

class MilestoneTile(BaseModel):
    title: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: A concise, impactful title that captures the essence of the accomplishment or next step (3-4 words maximum).

        TITLE REQUIREMENTS:
        - Maximum 3-4 words for impact and memorability
        - Use action-oriented language for next steps
        - Use achievement language for accomplishments
        - Be specific rather than generic
        - Capture the core essence of what was achieved or needs to be done
        
        EXAMPLES:
        Accomplishments: "Creative Solution Approach", "Deep System Analysis", "Strategic Risk Assessment"
        Next Steps: "Strengthen Evidence Base", "Consider Multiple Perspectives", "Develop Counter-Arguments"
        
        AVOID:
        - Generic phrases like "Good Work" or "Improve Skills"
        - Overly long descriptive titles
        - Vague or unclear language"""
    )
    
    detail: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: A specific 1-2 sentence explanation that provides context and actionable information.

        FOR ACCOMPLISHMENTS:
        - Describe the specific moment or behavior when this was achieved
        - Reference concrete examples from the workout responses
        - Explain why this accomplishment is meaningful or noteworthy
        - Connect to broader skill development or learning
        - Be specific about what they did, not just that they did well
        
        FOR NEXT STEPS:
        - Provide clear, actionable guidance on implementation
        - Explain HOW to achieve this improvement, not just WHAT to improve
        - Connect to specific areas where this was needed in current workout
        - Give concrete strategies or approaches they can use
        - Make it immediately applicable to their next workout
        
        QUALITY STANDARDS:
        - Be specific and evidence-based, avoid generic statements
        - Reference actual workout content when relevant
        - Provide actionable insights that can be immediately applied
        - Balance recognition with constructive guidance
        - Focus on observable, measurable improvements
        
        LENGTH: 1-2 sentences maximum for clarity and impact"""
    )
    
    model_config = {
        "arbitrary_types_allowed": True
    }