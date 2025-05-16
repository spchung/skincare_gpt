'''
Other intent shoudld be handled with suggested questions to ask the user.
'''
from pydantic import Field
from app.internal.client import llm
import instructor
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from app.lang_graphs.chat_v1.models.state import State
from langchain_core.messages import AIMessage


class OtherIntentInputSchema(BaseIOSchema):
    """ OtherIntentInputSchema """
    query: str = Field(None, description="The user's query.")

class OtherIntentOutputSchema(BaseIOSchema):
    """ OtherIntentOutputSchema """
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
        temperature=0,
        input_schema=OtherIntentInputSchema,
        output_schema=OtherIntentOutputSchema,
        system_prompt_generator=prompt,
    ),
)

def other_handler(state: State):
    res = worker.run(OtherIntentInputSchema(query=state['messages'][-1].content))
    return {
        "messages": [AIMessage(content=res.response)],
    }
