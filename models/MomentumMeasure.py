from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.HistoryTile import HistoryTile

class MomentumMeasure(BaseModel):
    last_workout: Optional[List[HistoryTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Extract momentum indicators from the user's immediately previous workout.

        DATA EXTRACTION PROCESS:
        1. Identify all strength spotlights (positive feedback) from the last workout's "Neural Power" assessment
        2. Identify all constructive criticisms (areas for improvement) from the last workout
        3. For each item, create a HistoryTile with:
           - title: Extract the exact title/topic of the feedback
           - hasImplemented: Analyze current workout to determine if this feedback was addressed
        
        IMPLEMENTATION ASSESSMENT CRITERIA:
        - Compare previous feedback recommendations with current workout responses
        - Look for evidence that user applied previous suggestions
        - Mark true if user demonstrates reasonable progress on that feedback area
        - Mark false if no evidence of implementation or improvement is observed
        
        FOCUS ON: Performance trends, skill development, and behavioral changes since last workout."""
    )
    
    within_team: Optional[List[HistoryTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Analyze momentum patterns across all workouts within the current team/context.

        DATA ANALYSIS SCOPE:
        1. Review feedback patterns across all workouts in this specific team
        2. Identify recurring strength spotlights that show consistent performance
        3. Identify recurring constructive criticisms that may indicate persistent areas for growth
        4. Track implementation of feedback over multiple workouts within this team
        
        PATTERN RECOGNITION:
        - Look for feedback themes that appear multiple times
        - Assess whether user is consistently working on team-specific skills
        - Evaluate progress on team-related challenges over time
        - Identify team-context specific momentum (building, stable, declining)
        
        OUTPUT: Create HistoryTiles for significant feedback patterns with implementation status based on current workout."""
    )

    across_everything: Optional[List[HistoryTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Evaluate long-term momentum patterns across the user's entire workout history.

        COMPREHENSIVE ANALYSIS SCOPE:
        1. Review feedback from all teams and all historical workouts
        2. Identify overarching skill development trends across all contexts
        3. Track fundamental strengths that appear consistently across different teams
        4. Identify core areas for improvement that persist across all workout contexts
        
        LONG-TERM PATTERN IDENTIFICATION:
        - Persistent strengths that show up regardless of team or context
        - Fundamental challenges that need sustained attention across all areas
        - Overall cognitive skill development trajectory
        - Universal feedback themes that transcend specific workout contexts
        
        IMPLEMENTATION TRACKING:
        - Assess whether fundamental feedback has been addressed over time
        - Look for evidence of sustained improvement on core skills
        - Identify areas where user has made lasting behavioral changes
        
        OUTPUT: Create HistoryTiles for the most significant long-term patterns with implementation assessment."""
    )

    model_config = {
        "arbitrary_types_allowed": True
    }