from pydantic import BaseModel, Field
from typing import Optional
from .Skill import Skill

class WorkoutRound(BaseModel):
    round_number: Optional[int] = Field(
        default=None,
        description="""REQUIRED: The sequential number of this workout round (1, 2, 3, etc.).

        NUMBERING REQUIREMENTS:
        - Start with 1 for the first round
        - Increment sequentially for each subsequent round
        - Must correspond to actual round structure in workout data
        - Use consistent numbering across all WorkoutRound objects in the list"""
    )
    
    skill: Optional[Skill] = Field(
        default=None, 
        description="""REQUIRED: Complete Neural Power skill assessment for this specific round.

        ROUND-SPECIFIC ASSESSMENT:
        - Evaluate user's performance ONLY within this specific round
        - Base assessment on responses, decisions, and behaviors from this round only
        - Follow the complete skill hierarchy structure (Neural Power → Level 2 → Level 3)
        - Provide round-specific evidence and examples in feedback
        
        SKILL ASSESSMENT SCOPE:
        - Assess all levels of the Neural Power hierarchy for this round
        - Include specific strength_spotlights and wisdom_whispers based on round performance
        - Reference actual round content in evidence fields
        - Focus on behaviors and patterns observable within this round
        
        PROGRESSION TRACKING:
        - Consider this as one data point in overall skill development
        - Identify round-specific improvements or challenges
        - Note any skill evolution within this round
        
        FORMATTING REQUIREMENTS:
        - Use complete Skill structure with all required fields
        - Provide round-specific evidence and examples
        - Maintain consistency with overall workout assessment while focusing on round-specific insights"""
    )
    
    model_config = {
        "arbitrary_types_allowed": True
    }