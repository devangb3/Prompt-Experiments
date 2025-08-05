from pydantic import BaseModel, Field
from typing import List, Optional
from .Skill import Skill
from .MomentumMeasure import MomentumMeasure
from .ReasoningRefinement import ReasoningRefinement
from .tiles.MilestoneTile import MilestoneTile
from .WorkoutRound import WorkoutRound

class BrainWorkoutResult(BaseModel):
    accomplishments: Optional[List[MilestoneTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Generate exactly 3 accomplishments that the user achieved during this workout.

        ACCOMPLISHMENT TYPES (choose from both categories):
        1. STRATEGY-BASED: How the user approached problems creatively or effectively
           - Novel problem-solving methods they used
           - Effective reasoning strategies they employed
           - Creative connections they made between concepts
        
        2. CONTENT-BASED: What the user demonstrated through their answers
           - Deep insights or understanding they showed
           - Interesting perspectives they brought up
           - Quality of analysis or reasoning they displayed

        FORMATTING REQUIREMENTS:
        - Each accomplishment must use MilestoneTile format (title + detail)
        - Focus on specific, observable behaviors from this workout
        - Make accomplishments feel meaningful and motivating
        - Avoid generic praise; be specific about what they did well"""
    )

    skills: Optional[Skill] = Field(
        default=None, 
        description="""CRITICAL: Generate a complete 3-level hierarchical skill assessment following this EXACT structure.

        MANDATORY HIERARCHY (must match exactly):
        Level 1 (Root): "Neural Power"
        ├── Level 2: "Critical Reasoning"
        │   ├── Level 3: "Information Understanding"
        │   ├── Level 3: "Argument Understanding" 
        │   └── Level 3: "Argument Creation"
        ├── Level 2: "Decision Making"
        │   ├── Level 3: "Decision Goal Setting"
        │   └── Level 3: "Decision Comparison"
        └── Level 2: "Communication"
            ├── Level 3: "Intent Matching"
            └── Level 3: "Clarity"

        ASSESSMENT REQUIREMENTS FOR EACH SKILL:
        1. LEAF SKILLS (Level 3): Assess based on direct evidence from user's workout responses
           - Provide specific score_explanation based on observed performance
           - Include 1-2 strength_spotlights (what they did well)
           - Include 1-2 wisdom_whispers (areas for improvement)
        
        2. PARENT SKILLS (Level 2 & 1): Summarize from children
           - score_explanation must synthesize assessments from direct children
           - strength_spotlights must reflect common themes from children's strengths
           - wisdom_whispers must identify overarching improvement areas from children
        
        3. ROOT SKILL ("Neural Power"): Overall synthesis
           - Provide holistic view of user's cognitive performance
           - Integrate insights from all three Level 2 skills

        CRITICAL: Every skill node must have complete data (name, explanation, spotlights, whispers, sub_skills)."""
    )

    momentum_measure: Optional[MomentumMeasure] = Field(
        default=None, 
        description="""REQUIRED: Assess user's performance momentum across three time horizons.

        ANALYSIS SCOPE:
        1. LAST WORKOUT: Compare current performance to their immediately previous workout
        2. WITHIN TEAM: Analyze trends across all workouts in current team/context
        3. ACROSS EVERYTHING: Evaluate patterns across all historical workout data

        DATA SOURCES TO USE:
        - Current workout responses and performance
        - Historical workout data provided in request
        - Previous feedback and skill assessments
        - Implementation of past recommendations

        OUTPUT REQUIREMENTS:
        - Extract specific titles from strength spotlights and constructive criticisms
        - Focus on observable improvements or declines
        - Identify momentum patterns (building, maintaining, declining)
        - Provide evidence-based momentum assessment"""
    )

    reasoning: Optional[ReasoningRefinement] = Field(
        default=None,
        description="""REQUIRED: Analyze the user's reasoning quality and identify specific areas for refinement.

        FOCUS AREAS:
        1. Missing perspectives they should have considered
        2. Unclear or problematic assumptions in their reasoning
        3. Logical flaws or gaps in their arguments
        4. Opportunities for more creative or original thinking

        BASE ANALYSIS ON:
        - Actual responses from this workout
        - Patterns in their reasoning approach
        - Missed opportunities for deeper analysis
        - Areas where thinking could be more rigorous or innovative"""
    )

    next_steps: Optional[List[MilestoneTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Synthesize actionable next steps from skill feedback and reasoning refinement.

        CONSOLIDATION PROCESS:
        1. Extract all improvement recommendations from:
           - Skill wisdom_whispers across all levels
           - Reasoning refinement suggestions (blind spots, assumptions, logic, creativity)
        
        2. Identify common themes and patterns
        
        3. Merge related recommendations into unified action items
        
        4. Prioritize by impact and feasibility
        
        FORMATTING REQUIREMENTS:
        - Create 2-4 consolidated next steps as MilestoneTiles
        - Each next step should be specific and actionable
        - Include clear implementation guidance in detail field
        - Focus on high-impact improvements for next workout"""
    )

    workout_rounds: Optional[List[WorkoutRound]] = Field(
        default_factory=list,
        description="""REQUIRED: Provide round-by-round skill assessment if workout has multiple rounds.

        FOR EACH ROUND:
        - Assess Neural Power skill development in that specific round
        - Track skill progression across rounds
        - Identify round-specific strengths and areas for improvement
        """
    )

    model_config = {
        "arbitrary_types_allowed": True
    } 