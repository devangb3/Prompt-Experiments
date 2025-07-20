class PromptCreator:
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template

    def create_prompt(self, framing_1=None, analytical_task=None, brain_data_sample=None, analytical_task_2=None, user_context_1=None, exrcise_context_1=None, output_structure=None) -> str:
        """
        Create a prompt by formatting the template with the provided keyword arguments.
        
        :param kwargs: Keyword arguments to format the prompt template.
        :return: Formatted prompt string.
        """

        defaults = {
            'LLM_FRAMING_1': "You are a professional, best-of-world-class, speech and debate coach with expertise in public speaking, speech and debate, emotional intelligence, growth mindset, design thinking and open strategy.",
            'LLM_ANALYTICAL_TASK_1': "Analyze the multi-modal data provided which contains",
            'BRAIN_DATA_SAMPLE': (
                "1. Facial emotion analysis over time\n"
                "2. Vocal burst analysis over time\n"
                "3. Speech prosody analysis over time\n"
                "4. Transcript of statements"
            ),
            'LLM_ANALYTICAL_TASK_2': (
                "Based on this multimodal data, analyze and provide specific Benefits, Opportunities, Risks, Challenges, Strengths, Weaknesses and "
                "Actionable Recommendations on how to improve the presentation performance.\n"
                "Focus on:\n"
                "- Facial expressions\n"
                "- Language usage and expression\n"
                "- Vocal delivery and tone\n"
                "- Body language\n"
                "- Content organization and clarity\n"
                "- Argumentation\n"
                "- Logic"
            ),
            'USER_CONTEXT_1': (
                "The multi-modal data is created from a speech and debate student speaker in high school whose goals are to educate and persuade the audience to take a For or Against position."
            ),
            'EXERCISE_CONTEXT_1': (
                "The multi-modal data is created from an activity to educate the layperson audience about a certain topic and persuade them to take a For or Against position."
            ),
            'OUTPUT_STRUCTURE_2': (
                "Format your response in clear, structured sections of Benefits, Opportunities, Risks, Challenges, Strengths, Weaknesses and Actionable Recommendations.\n"
                "Be specific, constructive, and encouraging. Limit your response to 300 words emphasizing Actionable Recommendations and do not generate markdown."
            )
        }

        LLM_FRAMING_1 = framing_1 or defaults['LLM_FRAMING_1']
        LLM_ANALYTICAL_TASK_1 = analytical_task or defaults['LLM_ANALYTICAL_TASK_1']
        BRAIN_DATA_SAMPLE = brain_data_sample or defaults['BRAIN_DATA_SAMPLE']
        LLM_ANALYTICAL_TASK_2 = analytical_task_2 or defaults['LLM_ANALYTICAL_TASK_2']
        USER_CONTEXT_1 = user_context_1 or defaults['USER_CONTEXT_1']
        EXERCISE_CONTEXT_1 = exrcise_context_1 or defaults['EXERCISE_CONTEXT_1']
        OUTPUT_STRUCTURE_2 = output_structure or defaults['OUTPUT_STRUCTURE_2']

        prompt = self.prompt_template.format(
            LLM_FRAMING_1=LLM_FRAMING_1,
            LLM_ANALYTICAL_TASK_1=LLM_ANALYTICAL_TASK_1,
            BRAIN_DATA_SAMPLE=BRAIN_DATA_SAMPLE,
            LLM_ANALYTICAL_TASK_2=LLM_ANALYTICAL_TASK_2,
            USER_CONTEXT_1=USER_CONTEXT_1,
            EXERCISE_CONTEXT_1=EXERCISE_CONTEXT_1,
            OUTPUT_STRUCTURE_2=OUTPUT_STRUCTURE_2,
        )

        return prompt

    def get_system_prompt(self) -> str:
        """
        Get the system prompt from the template.
        
        :return: System prompt string.
        """
        
        return self.create_prompt(
            framing_1=None,
            analytical_task=None,
            brain_data_sample=None,
            analytical_task_2=None,
            user_context_1=None,
            exrcise_context_1=None,
            output_structure=None
        )