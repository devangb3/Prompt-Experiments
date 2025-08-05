from pydantic import BaseModel, Field
from typing import List, Optional
from .tiles.FeedbackTile import FeedbackTile

class ReasoningRefinement(BaseModel):
    
    blind_spots: Optional[List[FeedbackTile]] = Field(
        default_factory=list, 
        description="""REQUIRED: Identify missing perspectives in the user's reasoning, formatted as constructive critique FeedbackTiles.

        BLIND SPOT IDENTIFICATION:
        1. PERSPECTIVE GAPS: Important viewpoints the user failed to consider
           - Alternative stakeholder perspectives
           - Different cultural, social, or economic angles
           - Opposing arguments or counterpoints
           - Broader systemic considerations
        
        2. ANALYTICAL GAPS: Dimensions of analysis that were overlooked
           - Missing cause-and-effect relationships
           - Unexamined assumptions about context
           - Ignored long-term or short-term implications
           - Overlooked interdependencies or trade-offs
        
        FEEDBACK FORMATTING:
        - Frame as constructive criticism, not compliments
        - Focus on what perspectives SHOULD HAVE BEEN included
        - Explain WHY these perspectives matter for complete analysis
        - Provide specific examples of how including these would strengthen reasoning
        
        EVIDENCE REQUIREMENT: Base critique on actual gaps observed in user's workout responses."""
    )

    unclear_assumptions: Optional[List[str]] = Field(
        default_factory=list, 
        description="""REQUIRED: Identify problematic assumptions in the user's reasoning (1-2 sentences each).

        ASSUMPTION ANALYSIS CATEGORIES:
        1. VAGUE ASSUMPTIONS: Statements that lack clarity or precision
           - Undefined terms or concepts
           - Ambiguous cause-and-effect claims
           - Imprecise generalizations
        
        2. FACTUALLY QUESTIONABLE: Claims that may not be accurate
           - Statements presented as fact without evidence
           - Outdated information or misconceptions
           - Overgeneralized statistics or trends
        
        3. CONTEXTUALLY INAPPROPRIATE: Assumptions that don't always hold
           - Context-dependent claims treated as universal
           - Assumptions that work in some situations but not others
           - Time-sensitive assumptions treated as permanent
        
        DOCUMENTATION FORMAT:
        - Quote or paraphrase the specific assumption from user's response
        - Explain why it's problematic (vague/wrong/contextual)
        - Suggest what clarification or evidence would strengthen it
        
        FOCUS: Assumptions that significantly impact the quality of their reasoning."""
    )

    logic_issues: Optional[List[str]] = Field(
        default_factory=list, 
        description="""REQUIRED: Identify logical flaws in the user's reasoning structure (1-2 sentences each).

        LOGICAL FLAW CATEGORIES:
        1. EVIDENCE PROBLEMS:
           - Missing evidence for key claims
           - Insufficient evidence to support conclusions
           - Irrelevant evidence that doesn't support the argument
           - Cherry-picked evidence that ignores contradicting data
        
        2. REASONING FLAWS:
           - Non-sequitur conclusions (doesn't follow from premises)
           - False cause-and-effect relationships
           - Overgeneralization from limited examples
           - Circular reasoning or begging the question
        
        3. STRUCTURAL ISSUES:
           - Unclear argument progression or organization
           - Missing crucial steps in logical chain
           - Contradictory statements within the same argument
           - Failure to address obvious counterarguments
        
        DOCUMENTATION FORMAT:
        - Identify the specific logical error type
        - Quote or reference the problematic reasoning
        - Explain how the logic fails and what would fix it
        
        PRIORITY: Focus on flaws that significantly undermine the argument's validity."""
    )

    creativity_issues: Optional[List[str]] = Field(
        default_factory=list, 
        description="""REQUIRED: Identify missed opportunities for more original and innovative thinking (1-2 sentences each).

        CREATIVITY GAP CATEGORIES:
        1. CONVENTIONAL THINKING: Over-reliance on standard approaches
           - Defaulting to obvious or common solutions
           - Following predictable analytical frameworks
           - Missing opportunities for novel connections
           - Staying within conventional boundaries when innovation was possible
        
        2. RISK AVERSION: Avoiding bold or original ideas
           - Presenting only "safe" or widely accepted viewpoints
           - Failing to explore unconventional possibilities
           - Missing opportunities to challenge assumptions
           - Not considering creative alternatives or solutions
        
        3. SURFACE-LEVEL ANALYSIS: Lack of depth in original thinking
           - Stopping at first-level insights instead of digging deeper
           - Missing opportunities for unique synthesis of ideas
           - Failing to make innovative connections between concepts
           - Not pushing beyond obvious implications
        
        DOCUMENTATION FORMAT:
        - Describe the specific area where more creativity was needed
        - Explain what type of original thinking was missing
        - Suggest what more innovative approach could have been taken
        
        FOCUS: Areas where creative thinking would have significantly enhanced the analysis quality."""
    )

    model_config = {
        "arbitrary_types_allowed": True
    }