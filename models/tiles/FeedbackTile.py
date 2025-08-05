from pydantic import BaseModel, Field
from typing import Optional

class FeedbackTile(BaseModel):
    title: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: A concise, descriptive title that clearly summarizes the core feedback theme (3-6 words).

        TITLE REQUIREMENTS:
        - Capture the essence of the feedback in 3-6 words
        - Use clear, specific language that immediately conveys the topic
        - For strength spotlights: Use positive, achievement-oriented language
        - For wisdom whispers: Use constructive, growth-oriented language
        
        EXAMPLES:
        Strength Spotlights: "Systematic Problem Analysis", "Creative Connection Making", "Clear Argument Structure"
        Wisdom Whispers: "Evidence Depth Enhancement", "Alternative Perspective Integration", "Assumption Clarification"
        
        AVOID:
        - Generic titles like "Good Job" or "Needs Improvement"
        - Overly technical jargon without context
        - Vague or ambiguous language"""
    )
    
    detail: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: A clear, specific explanation of the feedback that connects to actual workout behavior.

        EXPLANATION REQUIREMENTS:
        - Describe the specific behavior, pattern, or approach observed
        - Reference concrete examples from the user's workout responses
        - Explain WHY this behavior is effective (strengths) or limiting (improvements)
        - Connect to broader skill development or learning objectives
        - Provide context for how this impacts overall performance
        
        FOR STRENGTH SPOTLIGHTS:
        - Highlight what specifically they did that was effective
        - Explain the positive impact of this behavior
        - Connect to skill mastery or learning objectives
        
        FOR WISDOM WHISPERS:
        - Identify the specific gap or area for improvement
        - Explain how this limitation affects their performance
        - Frame constructively as growth opportunity
        
        QUALITY STANDARDS:
        - Be specific and evidence-based, avoid generic statements
        - Reference actual workout content and responses
        - Balance recognition with constructive guidance
        - Use supportive, developmental language"""
    )
    
    importance: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: Explain the significance and impact of this feedback for the user's development.

        FOR STRENGTH SPOTLIGHTS (importance of continuing this behavior):
        - Explain how this strength contributes to overall skill mastery
        - Describe the positive outcomes when they consistently apply this approach
        - Connect to long-term learning and development benefits
        - Identify how this strength can be leveraged in other contexts
        
        FOR WISDOM WHISPERS (importance of addressing this improvement area):
        - Explain the potential limitations or risks of not addressing this area
        - Describe how improvement in this area would enhance overall performance
        - Connect to broader skill development and learning objectives
        - Identify the compounding benefits of focusing on this improvement
        
        FOCUS AREAS:
        - Impact on learning effectiveness and skill development
        - Connection to real-world application and transfer
        - Relationship to overall cognitive and reasoning capabilities
        - Long-term benefits for continued growth and mastery"""
    )
    
    next_steps: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: Specific, actionable guidance for what the user should do going forward.

        FOR STRENGTH SPOTLIGHTS (what to keep doing or build upon):
        - Provide specific strategies for continuing this effective behavior
        - Suggest ways to deepen or expand this strength
        - Recommend how to apply this strength in new contexts or situations
        - Give concrete actions for building on this foundation
        
        FOR WISDOM WHISPERS (what to change or implement):
        - Provide clear, specific steps for addressing the improvement area
        - Suggest practical strategies and techniques they can use
        - Recommend resources, approaches, or methods for development
        - Give concrete actions they can take in their next workout
        
        ACTIONABILITY REQUIREMENTS:
        - Be specific enough that they know exactly what to do
        - Provide practical strategies they can implement immediately
        - Focus on behaviors and approaches within their control
        - Connect to their current skill level and development stage
        - Make recommendations achievable and realistic"""
    )
    
    reflection_question: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: A thought-provoking question to guide self-reflection and application in future workouts.

        QUESTION DESIGN PRINCIPLES:
        - Formulate as a question they should ask themselves while working
        - Focus on promoting self-awareness and intentional application
        - Connect directly to the specific feedback area
        - Encourage ongoing self-monitoring and adjustment
        
        FOR STRENGTH SPOTLIGHTS:
        - Help them recognize when they're applying this strength effectively
        - Guide them to consciously leverage this strength in new situations
        - Promote awareness of opportunities to use this strength
        
        FOR WISDOM WHISPERS:
        - Guide them to catch themselves when falling into limiting patterns
        - Prompt them to consider the improvement area during their work
        - Encourage proactive application of the suggested changes
        
        QUESTION FORMATS:
        - "As you analyze this problem, ask yourself: '...'"
        - "While developing your response, consider: '...'"
        - "Before finalizing your answer, reflect: '...'"
        - "During your reasoning process, check: '...'"
        
        QUALITY STANDARDS:
        - Make questions specific to the feedback topic
        - Ensure questions are practical and actionable during work
        - Focus on real-time self-monitoring and adjustment
        - Promote deeper thinking and awareness"""
    )
    
    evidence: Optional[str] = Field(
        default=None, 
        description="""REQUIRED: Specific quotes, examples, or references from the workout that demonstrate this feedback.

        EVIDENCE REQUIREMENTS:
        - Quote specific phrases, sentences, or passages from their responses
        - Reference particular moments or decisions that illustrate the feedback
        - Provide concrete examples that clearly support the feedback assessment
        - Use actual language and content from their workout submissions
        
        FOR STRENGTH SPOTLIGHTS:
        - Quote sections that demonstrate the effective behavior or approach
        - Reference specific instances where they applied this strength well
        - Highlight examples that show mastery or excellent application
        
        FOR WISDOM WHISPERS:
        - Quote sections that illustrate the improvement opportunity
        - Reference specific instances where the gap or limitation was evident
        - Highlight examples that demonstrate the need for development
        
        EVIDENCE QUALITY:
        - Use direct quotes whenever possible for maximum specificity
        - Provide enough context so the evidence is clear and meaningful
        - Select the most representative examples that clearly support the feedback
        - Ensure evidence directly connects to and supports the feedback message
        - Balance brevity with sufficient detail for clarity"""
    )

    model_config = {
        "arbitrary_types_allowed": True
    }