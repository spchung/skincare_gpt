from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from pydantic import Field  
from app.internal.client import llm
import instructor
from typing import Literal

class OtherIntentClassifierInputSchema(BaseIOSchema):
    """ OtherIntentClassifierInputSchema """
    query: str = Field(None, description="The user's query.")

class OtherIntentClassifierOutputSchema(BaseIOSchema):
    """ OtherIntentClassifierOutputSchema """
    intent: Literal["greeting", "unknown"] = Field(None, description="The intent of the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a lightweight intent classifier designed to handle miscellaneous queries that do not fall into predefined intent categories.",
        "Your specific job is to detect whether a user's query is a greeting (e.g., 'hi', 'hello', 'good morning') or something that cannot be classified ('unknown').",
        "This classifier operates as part of a larger intent-routing system. If the query doesn't clearly express a greeting, it should be classified as 'unknown'."
    ],
    steps=[
        "Read the user's query carefully.",
        "Check if the query is a clear greeting, such as a salutation, welcome, or polite opening message.",
        "If the message contains a mix of content but starts with a greeting, consider whether the primary purpose is still a greeting or if it expresses another unknown intent.",
        "Avoid over-classifying: only classify as 'greeting' if it unmistakably fits that category.",
    ],
    output_instructions=[
        "If the user's query is a greeting, output 'greeting' as the intent.",
        "If the user's query does not clearly indicate a greeting, output 'unknown' as the intent.",
        "Do not guess or infer any intent beyond 'greeting' or 'unknown'."
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        temperature=0,
        input_schema=OtherIntentClassifierInputSchema,
        output_schema=OtherIntentClassifierOutputSchema,
        system_prompt_generator=prompt,
    ),
)