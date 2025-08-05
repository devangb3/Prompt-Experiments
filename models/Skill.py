from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.FeedbackTile import FeedbackTile

class Skill(BaseModel):
    skill_name: Optional[str] = Field(
        default=None,
        description="""REQUIRED: The exact name of the skill being assessed.

        NAMING REQUIREMENTS:
        - Use the exact skill names from the mandated hierarchy
        - For leaf skills: Must match prescribed Level 3 skill names
        - For parent skills: Must match prescribed Level 2 skill names  
        - For root skill: Must be exactly "Neural Power"
        
        SKILL HIERARCHY REFERENCE:
        Level 1: "Neural Power"
        Level 2: "Critical Reasoning", "Decision Making", "Communication"
        Level 3: "Information Understanding", "Argument Understanding", "Argument Creation", 
                "Decision Goal Setting", "Decision Comparison", "Intent Matching", "Clarity" """
    )
    
    score_explanation: Optional[str] = Field(
        default=None,
        description="""REQUIRED: Clear explanation of the skill assessment and score.

        FOR LEAF SKILLS (Level 3):
        - Base assessment on direct evidence from user's workout responses
        - Describe specific behaviors or patterns observed
        - Connect observations to skill definition and expectations
        - Provide concrete examples from their answers
        - Explain both strengths and areas for improvement in this skill
        
        FOR PARENT SKILLS (Level 2 & Root):
        - Synthesize assessment from direct child skills
        - Identify overarching patterns across child skill assessments
        - Highlight the most significant strengths and improvement areas
        - Explain how child skills contribute to overall performance in parent skill
        - Provide holistic view while referencing specific child skill insights
        
        QUALITY STANDARDS:
        - Be specific and evidence-based, avoid generic statements
        - Focus on observable behaviors and patterns
        - Balance recognition of strengths with constructive areas for growth
        - Make assessment actionable and clear"""
    )
    
    strength_spotlights: Optional[List[FeedbackTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Constructive compliments highlighting what the user did well in this skill area.

        IDENTIFICATION CRITERIA:
        - Specific behaviors they demonstrated that align with skill excellence
        - Effective strategies or approaches they used
        - Quality insights or reasoning they showed
        - Evidence of skill application that should be reinforced
        
        FEEDBACK QUALITY STANDARDS:
        - Be specific about what they did, not just that they did well
        - Reference concrete examples from their workout responses
        - Explain why this behavior/approach is effective
        - Encourage continuation and further development of these strengths
        - Connect to broader skill development trajectory
        
        FORMATTING REQUIREMENTS:
        - Use FeedbackTile format with complete fields
        - Include evidence field with specific quotes or examples
        - Provide actionable next_steps for building on strengths
        - Frame as positive reinforcement, not just praise
        
        TARGET: 1-2 high-quality spotlights per skill that truly capture their best work."""
    )
    
    wisdom_whispers: Optional[List[FeedbackTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Constructive criticism identifying areas for improvement in this skill.

        IDENTIFICATION CRITERIA:
        - Specific behaviors or patterns that need refinement
        - Missed opportunities for better skill application
        - Areas where they fell short of skill expectations
        - Gaps between current performance and skill mastery
        
        CONSTRUCTIVE FRAMING:
        - Focus on what they should START doing or do DIFFERENTLY
        - Avoid negative language; frame as growth opportunities
        - Provide clear, actionable guidance for improvement
        - Connect criticism to specific skill development goals
        - Balance challenge with encouragement
        
        EVIDENCE-BASED FEEDBACK:
        - Reference specific examples from workout responses
        - Quote relevant portions that demonstrate the gap
        - Explain why the current approach limits effectiveness
        - Show how improvement would enhance overall performance
        
        FORMATTING REQUIREMENTS:
        - Use FeedbackTile format with complete, thoughtful fields
        - Include specific evidence and clear next_steps
        - Provide reflection_question to guide future application
        - Frame as supportive guidance, not criticism
        
        TARGET: 1-2 high-impact improvement areas that will meaningfully advance their skill."""
    )
    
    sub_skills: Optional[List['Skill']] = Field(
        default_factory=list,
        description="""REQUIRED: List of child skills for non-leaf nodes in the skill hierarchy.

        HIERARCHY REQUIREMENTS:
        - ONLY populate for Level 1 (Neural Power) and Level 2 skills (Critical Reasoning, Decision Making, Communication)
        - LEAVE EMPTY for Level 3 leaf skills
        
        CHILD SKILL REQUIREMENTS:
        - Each child must be a complete Skill object with all fields populated
        - Follow exact hierarchy structure specified in BrainWorkoutResult
        - Ensure parent-child relationships match prescribed skill tree
        
        ASSESSMENT CONSISTENCY:
        - Parent skill assessments must synthesize from child assessments
        - Maintain coherent narrative across skill hierarchy levels
        - Ensure child skill feedback supports parent skill conclusions"""
    )

    model_config = {
        "arbitrary_types_allowed": True
    }