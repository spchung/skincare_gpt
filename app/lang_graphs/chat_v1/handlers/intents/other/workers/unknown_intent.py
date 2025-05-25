from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from pydantic import Field  
from app.internal.client import llm
import instructor

class UnknownIntentInputSchema(BaseIOSchema):
    """ UnknownIntentInputSchema """
    query: str = Field(None, description="The user's query.")

class UnknownIntentOutputSchema(BaseIOSchema):
    """ UnknownIntentOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a helpful assistant in a skincare product chatbot.",
        "The user has submitted a query that does not match any known intent such as product search, review search, product comparison, or filtered product queries.",
        "Your task is to gently guide the user by suggesting example questions they can ask the chatbot.",
        "The goal is to educate the user about the chatbot’s capabilities in a clear, friendly, and non-repetitive manner."
    ],
    steps=[
        "Acknowledge that the chatbot didn't understand the user’s intent.",
        "Politely offer help by suggesting 2–3 example questions the user *can* ask.",
        "The examples should reflect the chatbot’s main capabilities: product discovery, review lookup, comparisons, and filtered searches (e.g., by ingredient, price, or SPF).",
        "Use a tone that is encouraging and user-friendly — not overly formal or mechanical."
    ],
    output_instructions=[
        "Do not include the user’s original query.",
        "Output a single friendly response with 2–3 well-phrased example questions.",
        "Avoid technical or system-level language — speak like a helpful assistant."
    ]
)

worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=UnknownIntentInputSchema,
        output_schema=UnknownIntentOutputSchema,
        system_prompt_generator=prompt,
    ),
)