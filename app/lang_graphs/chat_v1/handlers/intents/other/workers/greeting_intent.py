from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from pydantic import Field  
from app.internal.client import llm
import instructor

class GreetingIntentInputSchema(BaseIOSchema):
    """ GreetingIntentInputSchema """
    query: str = Field(None, description="The user's query.")

class GreetingIntentOutputSchema(BaseIOSchema):
    """ GreetingIntentOutputSchema """
    response: str = Field(None, description="The response to the user's query.")

prompt = SystemPromptGenerator(
    background=[
        "You are a helpful assistant in a skincare product chatbot.",
        "The user has submitted a greeting query.",
        "Your task is to greet the user and guide them to the chatbot's capabilities."
    ],
    steps=[
        "Greet the user with a friendly message.",
        "Introduce the chatbot's capabilities.",
        "Provide a brief overview of the chatbot's features and how to use it.",
        "Politely offer help by suggesting 2–3 example questions the user *can* ask.",
        "The examples should reflect the chatbot’s main capabilities: product discovery, review lookup, comparisons, and filtered searches (e.g., by ingredient, price, or SPF).",
        "Use a tone that is encouraging and user-friendly — not overly formal or mechanical."
    ],
    output_instructions=[
        "Do not include the user’s original query.",
        "Use a tone that is encouraging and user-friendly — not overly formal or mechanical."
        "Output a single friendly response with 2–3 well-phrased example questions.",
        "Avoid technical or system-level language — speak like a helpful assistant."
    ]
)
worker = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(llm),
        model='gpt-4o-mini',
        input_schema=GreetingIntentInputSchema,
        output_schema=GreetingIntentOutputSchema,
        system_prompt_generator=prompt,
    ),
)